# AutomatedWhatsApp-python
It is an automated WhatsApp with code in Python

This base version of the code repo can automate WhatsApp functions like:
1. sending messages
2. reading contact numbers from a text file and send them messages. 
3. attaching media like images, pdf files etc

The code is written in Python and makes use of selenium for control and automation

Pre-requisites: Web WhatsApp must be open - the code will scan the QR code the first time.

The requirements.txt file is created and put up in the repo and can be used with the command:
pip install -r requirements.txt 

for installing all the dependent packages.

Drawbacks:
1. It roughly takes a minute of time to send message to one person.

Use-case: 
1. Sending messages with media to unknown numbers - the number need not be saved as a contact.

Future features:
1. The time for sending messages can be reduced. Be careful not to reduce the time to drastic low values - the UI may not load properly.
2. Different kinds of media can be attached.
3. The contacts can be read from other files like an excel file or a csv file.

# Please note: 
1. The UI elements of WhatsApp keep changing - internally and may not be fetched properly by the selenium part of the code. 
2. There are some cases - when the media does not get attached - but only sends the message.  

# Additional Setup (if needed):
1. Chrome Browser: Make sure you have Google Chrome installed
Download from: https://www.google.com/chrome/
2. Chrome Driver: The webdriver-manager will automatically download the correct ChromeDriver version, so you don't need to manually install it.
