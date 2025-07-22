import pywhatkit as kit
import time

# Predefined contacts (Modify as needed)
contacts = {
    "john": "+911234567890",
    "emma": "+919876543210",
    "nancy": "+919027284016",
    "mehak": "+917206550805"
}

# Ask user for recipient name
recipient_name = input("Enter the name of the person you want to message: ").strip().lower()

# Check if contact exists before proceeding
if recipient_name in contacts:
    phone_number = contacts[recipient_name]  # Get the phone number
    print(f"✅ Contact found: {recipient_name.capitalize()} ({phone_number})")

    # Ask for the message
    message = input(f"Enter the message to send to {recipient_name.capitalize()}: ").strip()

    # Ensure message is not empty
    while not message:
        print("❌ Message cannot be empty!")
        message = input(f"Enter the message to send to {recipient_name.capitalize()}: ").strip()

    # Ask for confirmation
    confirm = input(f"Send this message to {recipient_name.capitalize()}? (yes/no): ").strip().lower()
    
    if confirm in ['yes', 'y']:
        try:
            print("📤 Sending message... Please wait.")
            time.sleep(2)  # Small delay for stability

            # Ensure WhatsApp Web is open
            kit.sendwhatmsg_instantly(phone_number, message, wait_time=10)  # Increased wait time for stability
            
            print(f"✅ Message sent to {recipient_name.capitalize()} successfully!")
        except Exception as e:
            print(f"❌ An error occurred: {e}")
    else:
        print("❌ Message sending canceled.")
else:
    print("❌ Contact not found. Please check the name or add it to the list.")
