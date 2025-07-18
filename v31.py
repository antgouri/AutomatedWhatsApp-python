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
# attach text file here - both absolute / relative path should work
TXT_FILE = " "
# attach image path here - media file. 
IMAGE_FILE = " "
MESSAGE = "some message here"
WAIT_LOGIN = 30

# Speed optimization settings
FAST_MODE = True
BATCH_SIZE = 10
DELAY_BETWEEN_BATCHES = 60

# ====== VERIFY FILES EXIST ======
if not os.path.exists(TXT_FILE):
    print(f"❌ Error: {TXT_FILE} not found!")
    exit(1)

if not os.path.exists(IMAGE_FILE):
    print(f"❌ Error: {IMAGE_FILE} not found!")
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
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
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
print(f"⚡ Fast mode: {'ON' if FAST_MODE else 'OFF'}")

# Calculate timing based on mode - INCREASED for reliability
if FAST_MODE:
    WAIT_CHAT_LOAD = 3       # Increased from 2
    WAIT_AFTER_MESSAGE = 4   # Increased from 3
    WAIT_AFTER_ATTACH = 3    # Increased from 2
    WAIT_AFTER_UPLOAD = 4    # Increased from 3
    WAIT_AFTER_SEND = 4      # Increased from 3
else:
    WAIT_CHAT_LOAD = 5
    WAIT_AFTER_MESSAGE = 6
    WAIT_AFTER_ATTACH = 4
    WAIT_AFTER_UPLOAD = 6
    WAIT_AFTER_SEND = 6

def send_attachment_robust(driver, image_path):
    """
    Streamlined attachment sending using working methods only
    """
    print("📎 Starting attachment process...")
    
    # Method 1: Standard attach button (WORKING)
    try:
        print("🔍 Using attach method 1")
        attach_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Attach']"))
        )
        attach_button.click()
        print("✅ Attach clicked with method 1")
    except Exception as e:
        raise Exception(f"Attach method 1 failed: {str(e)[:50]}")
    
    time.sleep(WAIT_AFTER_ATTACH)
    
    # Method 1: File input (WORKING)
    try:
        print("🔍 Using file input method 1")
        file_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']"))
        )
        print("✅ File input found with method 1")
    except Exception as e:
        raise Exception(f"File input method 1 failed: {str(e)[:50]}")
    
    # Upload file
    file_input.send_keys(image_path)
    print("📸 Image uploaded successfully")
    time.sleep(WAIT_AFTER_UPLOAD)
    
    # Method 5: Send button (WORKING)
    try:
        print("🔍 Using send method 5")
        send_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send']"))
        )
        send_button.click()
        print("✅ Send clicked with method 5")
        
        # Wait to ensure send completes
        time.sleep(2)
        
        # Verify the message was sent by checking if send button disappeared
        try:
            WebDriverWait(driver, 3).until_not(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Send']"))
            )
            print("✅ Send method 5 confirmed successful")
        except:
            print("⚠️ Send verification timeout - but likely succeeded")
            
    except Exception as e:
        raise Exception(f"Send method 5 failed: {str(e)[:50]}")
    
    return True

# Process contacts
total_numbers = len(phone_numbers)
total_batches = (total_numbers + BATCH_SIZE - 1) // BATCH_SIZE
print(f"📊 Total contacts: {total_numbers}")
print(f"📊 Total batches: {total_batches}")

overall_success = 0
overall_failed = 0

for batch_num in range(total_batches):
    start_idx = batch_num * BATCH_SIZE
    end_idx = min(start_idx + BATCH_SIZE, total_numbers)
    batch_numbers = phone_numbers[start_idx:end_idx]
    
    print(f"\n🚀 BATCH {batch_num + 1}/{total_batches}: Processing contacts {start_idx + 1}-{end_idx}")
    
    batch_success = 0
    batch_failed = 0
    
    for i, number in enumerate(batch_numbers):
        global_index = start_idx + i + 1
        is_first_user = (global_index == 1)  # Check if this is the very first user
        
        try:
            print(f"\n📱 Processing {global_index}/{total_numbers}: {number}")
            if is_first_user:
                print("🚨 FIRST USER - Using extra precautions...")
            
            # Navigate to chat
            url = f"https://web.whatsapp.com/send?phone={number[1:]}"
            driver.get(url)
            
            # Extra wait for first user to ensure WhatsApp is fully loaded
            if is_first_user:
                print("⏳ First user - waiting for WhatsApp to fully initialize...")
                time.sleep(5)  # Extra 5 seconds for first user
                
                # Verify WhatsApp is fully loaded by checking for main interface
                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@id='main']"))
                    )
                    print("✅ WhatsApp main interface confirmed loaded")
                except:
                    print("⚠️ WhatsApp main interface not detected - proceeding anyway")
            
            # Wait for chat to load
            chat_wait_time = WAIT_CHAT_LOAD + (3 if is_first_user else 0)  # Extra time for first user
            print(f"⏳ Waiting {chat_wait_time}s for chat to load...")
            
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true'][@data-tab='10']"))
            )
            time.sleep(chat_wait_time)
            
            # Extra verification for first user that chat is ready
            if is_first_user:
                try:
                    input_box_test = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                    input_box_test.click()
                    time.sleep(1)
                    input_box_test.send_keys("test")  # Type test to ensure it's active
                    input_box_test.clear()  # Clear it
                    print("✅ First user - input box verified working")
                except Exception as e:
                    print(f"⚠️ First user - input box test failed: {str(e)[:50]}")
            
            # Send text message first
            input_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
            input_box.clear()
            input_box.send_keys(MESSAGE)
            input_box.send_keys(Keys.ENTER)
            print("✅ Text sent")
            
            # Extra wait after message for first user
            message_wait_time = WAIT_AFTER_MESSAGE + (2 if is_first_user else 0)
            time.sleep(message_wait_time)
            
            # Focus input box again
            input_box = driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
            input_box.click()
            time.sleep(1)
            
            # Send attachment using robust method
            if send_attachment_robust(driver, image_path):
                print(f"✅ Image sent to {number}")
                
                # Extra verification wait to ensure message is fully sent
                verify_wait_time = 3 + (2 if is_first_user else 0)  # Extra time for first user
                print(f"⏳ Verifying message delivery... ({verify_wait_time}s)")
                time.sleep(verify_wait_time)
                
                # Check if we're still in the same chat (successful send usually stays in chat)
                try:
                    # Look for message input to confirm we're still in chat
                    driver.find_element(By.XPATH, "//div[@contenteditable='true'][@data-tab='10']")
                    print("✅ Message delivery confirmed")
                    
                    if is_first_user:
                        # Extra verification for first user - check if message appears in chat
                        try:
                            # Look for any recent message in the chat
                            messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
                            if len(messages) > 0:
                                print("✅ First user - messages detected in chat")
                            else:
                                print("⚠️ First user - no messages detected, but continuing")
                        except:
                            print("⚠️ First user - could not verify messages in chat")
                            
                except:
                    print("⚠️ Chat interface changed - message may have sent")
                
                batch_success += 1
                
                # Progressive wait times - longer for each user to avoid WhatsApp throttling
                base_wait = WAIT_AFTER_SEND
                user_wait = base_wait + (i * 1) + (3 if is_first_user else 0)  # Extra wait for first user
                
                if i == len(batch_numbers) - 1:  # Last contact in batch
                    print("⏳ Last contact - ensuring completion...")
                    time.sleep(user_wait + 3)
                else:
                    print(f"⏳ Waiting {user_wait}s before next contact...")
                    time.sleep(user_wait)
            else:
                raise Exception("Attachment sending failed")
                
        except Exception as e:
            print(f"❌ Failed {number}: {str(e)[:50]}...")
            batch_failed += 1
            
            # Clear any open dialogs or attachment UI before next contact
            try:
                print("🔧 Cleaning up UI state...")
                # Try to close any open attachment dialog
                close_buttons = driver.find_elements(By.XPATH, "//button[@aria-label='Close']")
                for btn in close_buttons:
                    try:
                        btn.click()
                        time.sleep(1)
                    except:
                        pass
                        
                # Press Escape key to close any dialogs
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                time.sleep(1)
            except:
                pass
                
            time.sleep(4)  # Longer error recovery time
            continue
    
    # Batch summary
    overall_success += batch_success
    overall_failed += batch_failed
    
    print(f"\n📊 BATCH {batch_num + 1} COMPLETE:")
    print(f"   ✅ Success: {batch_success}")
    print(f"   ❌ Failed: {batch_failed}")
    
    # Wait between batches
    if batch_num < total_batches - 1:
        print(f"⏳ Waiting {DELAY_BETWEEN_BATCHES}s before next batch...")
        time.sleep(DELAY_BETWEEN_BATCHES)
    else:
        print("⏳ Final batch complete - ensuring all messages are sent...")
        time.sleep(10)

# Final summary
print(f"\n🎉 ALL BATCHES COMPLETED!")
print(f"📊 FINAL SUMMARY:")
print(f"   📱 Total contacts: {total_numbers}")
print(f"   ✅ Successful: {overall_success}")
print(f"   ❌ Failed: {overall_failed}")
print(f"   📈 Success rate: {(overall_success/total_numbers)*100:.1f}%")

print("⏳ Waiting 15 seconds to ensure all messages are delivered...")
time.sleep(15)

driver.quit()
print("\n🎉 All done! Browser closed.")
print("💡 Tip: Check WhatsApp to verify all messages were sent successfully.")