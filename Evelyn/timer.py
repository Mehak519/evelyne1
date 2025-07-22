import schedule
import time
import speech_recognition as sr
import pyttsx3
from datetime import datetime

# Initialize speech engine
engine = pyttsx3.init()

def speak(text):
    """Function to make Zira speak"""
    engine.say(text)
    engine.runAndWait()

def task(reminder_text):
    """Function to remind the user of a task"""
    print(f"Reminder: {reminder_text}")
    speak(f"Reminder: {reminder_text}")

def convert_to_24hr_format(time_str):
    """Converts 12-hour time format (with am/pm) to 24-hour format"""
    try:
        # Try to convert the 12-hour time format (with am/pm) to 24-hour format
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        return time_obj.strftime("%H:%M")  # Convert to 24-hour format (HH:MM)
    except ValueError:
        return None  # If the format is incorrect, return None

def recognize_speech():
    """Function to recognize voice commands for scheduling reminders"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for a reminder command...")
        speak("What should I remind you about?")
        
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")  # Log the entire recognized speech
            
            if "remind me to" in command:
                parts = command.replace("remind me to", "").strip().split(" at ")
                print(f"Parts: {parts}")  # Debugging log
                
                if len(parts) == 2:
                    reminder_text = parts[0].strip()
                    reminder_time = parts[1].strip()
                    
                    # Log the parsed reminder text and time
                    print(f"Reminder Text: {reminder_text}, Time: {reminder_time}")
                    
                    # Convert time to 24-hour format
                    reminder_time_24hr = convert_to_24hr_format(reminder_time)
                    print(f"Converted time: {reminder_time_24hr}")  # Debugging log
                    
                    if reminder_time_24hr:
                        # Schedule the task
                        schedule.every().day.at(reminder_time_24hr).do(task, reminder_text)
                        print(f"Reminder set for '{reminder_text}' at {reminder_time_24hr}!")
                        speak(f"Reminder set for {reminder_text} at {reminder_time_24hr}.")
                    else:
                        print("Sorry, I couldn't understand the time. Please try again.")
                        speak("Sorry, I didn't catch the time. Please try again.")
                else:
                    print("Sorry, I couldn't understand the time. Please try again.")
                    speak("Sorry, I didn't catch the time. Please try again.")

        except sr.UnknownValueError:
            print("Sorry, I couldn't understand. Please try again.")
            speak("Sorry, I couldn't understand. Please repeat.")
        except sr.RequestError:
            print("Could not request results. Check your internet connection.")
            speak("I couldn't process your request. Please check your internet.")

print("Zira is listening for reminders...")
speak("Hello! I'm ready to take your reminders.")

while True:
    recognize_speech()
    schedule.run_pending()  # Correct method for running scheduled tasks
    time.sleep(1)
