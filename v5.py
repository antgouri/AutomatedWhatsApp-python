import os
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ====== CONFIGURATION ======
TXT_FILE = "contacts_test.txt"
MESSAGE_FILE = "message.txt"
IMAGE_FILE = "invite.jpeg"
WAIT_LOGIN = 30

# ====== VERIFY FILES EXIST ======
if not os.path.exists(TXT_FILE):
    print(f"❌ Error: {TXT_FILE} not found!")
    exit(1)

if not os.path.exists(MESSAGE_FILE):
    print(f"❌ Error: {MESSAGE_FILE} not found!")
    exit(1)

if not os.path.exists(IMAGE_FILE):
    print(f"❌ Error: {IMAGE_FILE} not found!")
    exit(1)

# ====== LOAD MESSAGE FROM FILE ======
try:
    with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
        MESSAGE = f.read().strip()
    
    print(f"✅ Message loaded from {MESSAGE_FILE}")
    print(f"📏 Message length: {len(MESSAGE)} characters")
    print(f"📄 Message content:")
    print("-" * 50)
    print(MESSAGE)
    print("-" * 50)
    
    if len(MESSAGE) == 0:
        print("❌ Error: Message file is empty!")
        exit(1)
        
except FileNotFoundError:
    print(f"❌ Error: {MESSAGE_FILE} not found!")
    exit(1)
except Exception as e:
    print(f"❌ Error reading message file: {e}")
    exit(1)

# ====== LOAD NUMBERS ======
with open(TXT_FILE, "r") as f:
    raw_numbers = f.readlines()

phone_numbers = ["+91" + line.strip() for line in raw_numbers if line.strip().isdigit()]
print(f"📱 Loaded {len(phone_numbers)} phone numbers")

# ====== SETUP CHROME ======
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get("https://web.whatsapp.com")
print(f"📱 Please scan the QR code (waiting {WAIT_LOGIN}s)...")
time.sleep(WAIT_LOGIN)

image_path = os.path.abspath(IMAGE_FILE)
print(f"📸 Image path: {image_path}")

def send_message_as_single_block(driver, message):
    """
    Send message as single block - FIXED VERSION
    """
    try:
        # Find the input box
        input_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        input_box.click()
        time.sleep(1)
        
        # CLEAR the input box completely
        input_box.send_keys(Keys.CONTROL + "a")
        time.sleep(0.2)
        input_box.send_keys(Keys.DELETE)
        time.sleep(0.5)
        
        print(f"📝 Typing message: {message[:50]}...")
        
        # METHOD 1: Direct JavaScript insertion (most reliable)
        try:
            # Escape the message properly for JavaScript
            escaped_message = message.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
            
            js_script = f'''
            var element = arguments[0];
            element.innerHTML = '';
            element.textContent = "{escaped_message}";
            
            // Simulate typing to trigger WhatsApp's detection
            var event = new Event('input', {{ bubbles: true }});
            element.dispatchEvent(event);
            
            // Focus the element
            element.focus();
            '''
            
            driver.execute_script(js_script, input_box)
            print("✅ Message inserted via JavaScript")
            time.sleep(2)
            
            # Verify message was inserted
            current_text = input_box.get_attribute('textContent') or input_box.text
            if len(current_text) > 10:  # Check if message is there
                print(f"✅ Message verified in input box: {len(current_text)} characters")
                return True
            else:
                print("⚠️ JavaScript method didn't insert text properly")
                
        except Exception as e:
            print(f"⚠️ JavaScript method failed: {e}")
        
        # METHOD 2: Character by character with SHIFT+ENTER for newlines
        try:
            print("🔄 Trying fallback method...")
            input_box.clear()
            time.sleep(0.5)
            
            # Replace newlines with a placeholder, then send character by character
            lines = message.split('\n')
            for i, line in enumerate(lines):
                if line.strip():  # Only send non-empty lines
                    input_box.send_keys(line)
                    print(f"✅ Sent line {i+1}: {line[:30]}...")
                
                # Add line break if not the last line
                if i < len(lines) - 1:
                    input_box.send_keys(Keys.SHIFT + Keys.ENTER)
                    time.sleep(0.1)
            
            print("✅ Message typed with line breaks")
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"❌ Fallback method failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Failed to find input box: {e}")
        return False

def send_attachment(driver, image_path):
    """
    Send attachment using the working selectors
    """
    try:
        # Click attach button
        attach_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Attach']"))
        )
        attach_button.click()
        print("✅ Attach clicked")
        time.sleep(2)
        
        # Find file input
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']"))
        )
        file_input.send_keys(image_path)
        print("✅ Image uploaded")
        time.sleep(3)
        
        # Send button
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send']"))
        )
        send_button.click()
        print("✅ Image sent")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"❌ Attachment failed: {e}")
        return False

# Process each contact
for i, number in enumerate(phone_numbers, 1):
    try:
        print(f"\n🚀 Processing {i}/{len(phone_numbers)}: {number}")
        
        # Navigate to chat
        url = f"https://web.whatsapp.com/send?phone={number[1:]}"
        driver.get(url)
        
        # Wait for chat to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
        )
        time.sleep(3)
        
        # Send message as single block
        print(f"📝 Sending message to {number}...")
        print(f"📄 Message to send: {MESSAGE[:100]}{'...' if len(MESSAGE) > 100 else ''}")
        
        if send_message_as_single_block(driver, MESSAGE):
            print("✅ Message prepared successfully")
            
            # CRITICAL: Send the message with ENTER
            try:
                input_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                input_box.send_keys(Keys.ENTER)
                print("✅ Message SENT with ENTER key")
                time.sleep(4)
                
                # Verify message was sent by checking if input is empty
                current_text = input_box.get_attribute('textContent') or input_box.text
                if len(current_text.strip()) == 0:
                    print("✅ Message send confirmed - input box is now empty")
                else:
                    print(f"⚠️ Input box still has text: {current_text[:50]}...")
                
            except Exception as e:
                print(f"❌ Failed to send message with ENTER: {e}")
                continue
            
            # Send attachment
            if send_attachment(driver, image_path):
                print(f"✅ Complete message + image sent to {number}")
            else:
                print(f"⚠️ Message sent but attachment failed for {number}")
        else:
            print(f"❌ Message sending failed for {number}")
            
        time.sleep(5)  # Wait between contacts
        
    except Exception as e:
        print(f"❌ Failed for {number}: {e}")
        time.sleep(3)
        continue

driver.quit()
print("\n🎉 All done!")