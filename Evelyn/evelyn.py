import tkinter as tk
from PIL import Image, ImageTk
import speech_recognition as sr
import threading
from dotenv import load_dotenv
import os
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import random
import time
import pyautogui
import re
import cv2
import numpy as np
import math

# Function to Listen for Voice Commands
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[3].id)  # Adjust voice if needed
# Create a borderless transparent window

# Initialize the Window
root = tk.Tk()
root.title("Evelyn - AI Assistant")
root.attributes("-topmost", True)
root.overrideredirect(True)
root.config(bg="white")
root.wm_attributes("-transparentcolor", "white")

# Resize Dimensions
NEW_WIDTH, NEW_HEIGHT = 150, 150
SPEED = 3  # Smooth movement speed

# Load Images
image_paths = {
    "up": r"C:\Users\pj892\OneDrive\Desktop\Evelyn\TESTGUI.png",
    "down": r"C:\Users\pj892\OneDrive\Desktop\Evelyn\TESTGUI.png",
    "left": r"C:\Users\pj892\OneDrive\Desktop\Evelyn\TESTGUI.png",
    "right": r"C:\Users\pj892\OneDrive\Desktop\Evelyn\TESTGUI.png"
}

def process_image(path):
    img = Image.open(path).convert("RGBA").resize((NEW_WIDTH, NEW_HEIGHT))
    return ImageTk.PhotoImage(img)

images = {key: process_image(path) for key, path in image_paths.items()}

# Create Canvas
canvas = tk.Canvas(root, width=NEW_WIDTH, height=NEW_HEIGHT, bg="white", highlightthickness=0)
canvas.pack()

# Display Default Image
image_id = canvas.create_image(0, 0, anchor=tk.NW, image=images["right"])

# Get Screen Dimensions
root.update_idletasks()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Set Initial Position
start_x = screen_width - NEW_WIDTH - 50
start_y = screen_height - NEW_HEIGHT - 100
root.geometry(f"{NEW_WIDTH}x{NEW_HEIGHT}+{start_x}+{start_y}")
root.update()

# Movement Variables
direction = random.choice(["up", "down", "left", "right", "up-right", "down-right", "up-left", "down-left"])
last_move_time = time.time()
change_interval = random.uniform(3, 5)

# Dragging Variables
drag_data = {"x": 0, "y": 0, "is_dragging": False}

# Cursor Following Variables
is_following_cursor = False
cursor_follow_duration = 0
last_cursor_x, last_cursor_y = pyautogui.position()
cursor_shake_threshold = 50  # Minimum pixels moved rapidly to detect shaking
last_cursor_check_time = time.time()

# 🖱 Smooth Dragging Functions
def on_drag_start(event):
    drag_data["x"], drag_data["y"], drag_data["is_dragging"] = event.x_root, event.y_root, True

def on_drag_motion(event):
    if drag_data["is_dragging"]:
        new_x = root.winfo_x() + (event.x_root - drag_data["x"])
        new_y = root.winfo_y() + (event.y_root - drag_data["y"])
        root.geometry(f"+{new_x}+{new_y}")
        drag_data["x"], drag_data["y"] = event.x_root, event.y_root
        time.sleep(0.01)  # Smooth delay

def on_drag_release(event):
    drag_data["is_dragging"] = False

root.bind("<ButtonPress-1>", on_drag_start)
root.bind("<B1-Motion>", on_drag_motion)
root.bind("<ButtonRelease-1>", on_drag_release)

# 📷 Improved Obstacle Detection
def detect_obstacle(x, y):
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    # Use Canny Edge Detection to detect icons and text
    edges = cv2.Canny(img, threshold1=100, threshold2=200)

    # Brightness Thresholding (detects white text/icons)
    _, thresholded = cv2.threshold(img, 200, 255, cv2.THRESH_BINARY)

    # Combine both detections
    combined = cv2.bitwise_or(edges, thresholded)

    # Extract AI's region
    roi = combined[y:y+NEW_HEIGHT, x:x+NEW_WIDTH]

    # Count white pixels (indicating obstacles)
    return cv2.countNonZero(roi) > 500  # Avoids bright areas (icons, text, etc.)

# 🔄 Smooth Movement Function
cursor_positions = []  # Track last few cursor positions
cursor_shake_detected = False  # Flag for shaking
shake_start_time = 0  # Track when shaking starts
last_follow_end_time = 0  # Cooldown after following
shake_check_duration = 0.5  # Time window to detect shaking
follow_cooldown = 5  # Cooldown before following again
last_random_follow_time = 0  # Track last random follow time

def move_robot():
    global direction, last_move_time, change_interval
    global last_cursor_x, last_cursor_y, last_cursor_check_time
    global is_following_cursor, cursor_follow_duration
    global cursor_positions, cursor_shake_detected, shake_start_time, last_follow_end_time
    global last_random_follow_time  # Track last random follow

    current_time = time.time()
    x, y = root.winfo_x(), root.winfo_y()
    current_cursor_x, current_cursor_y = pyautogui.position()

    # Track last 0.5 sec of movements
    cursor_positions.append((current_cursor_x, current_cursor_y, current_time))
    cursor_positions = [pos for pos in cursor_positions if current_time - pos[2] < shake_check_duration]

    # Detect cursor shaking (rapid movement in a small area)
    if len(cursor_positions) >= 6:  # Ensure at least 6 movements in 0.5 sec
        min_x = min(pos[0] for pos in cursor_positions)
        max_x = max(pos[0] for pos in cursor_positions)
        min_y = min(pos[1] for pos in cursor_positions)
        max_y = max(pos[1] for pos in cursor_positions)

        if (max_x - min_x) < 40 and (max_y - min_y) < 40:  # Cursor moving rapidly in a small area
            if not cursor_shake_detected:
                cursor_shake_detected = True
                shake_start_time = current_time
                is_following_cursor = True
                cursor_follow_duration = random.uniform(5, 7)  # Follow for 5-7 sec

    else:
        cursor_shake_detected = False  # Reset if not detected

    # Stop following after the duration
    if is_following_cursor and (current_time - shake_start_time >= cursor_follow_duration):
        is_following_cursor = False
        last_follow_end_time = current_time  # Set cooldown

    # Ensure Evelyn doesn't follow again immediately after stopping
    if not is_following_cursor and (current_time - last_follow_end_time < follow_cooldown):
        is_following_cursor = False  # Prevent immediate re-follow

    # Randomly follow the cursor 1-2 times every 7-8 minutes
    if not is_following_cursor and (current_time - last_random_follow_time > random.randint(420, 480)):  # 7-8 min
        if random.random() < 0.5:  # 50% chance in that interval
            is_following_cursor = True
            cursor_follow_duration = random.uniform(5, 7)  # Follow for 5-7 sec
            last_random_follow_time = current_time  # Update last follow time

    # Move Evelyn based on the mode
    if is_following_cursor:
        step_x = (current_cursor_x - x) / 20
        step_y = (current_cursor_y - y) / 20
        new_x = x + step_x
        new_y = y + step_y
    else:
        # Random movement logic
        if current_time - last_move_time >= change_interval:
            direction = random.choice(["up", "down", "left", "right", "up-right", "down-right", "up-left", "down-left"])
            last_move_time = current_time
            change_interval = random.uniform(3, 7)

        if direction == "right":
            new_x, new_y = x + 2, y
        elif direction == "left":
            new_x, new_y = x - 2, y
        elif direction == "down":
            new_x, new_y = x, y + 2
        elif direction == "up":
            new_x, new_y = x, y - 2
        elif direction == "up-right":
            new_x, new_y = x + 2, y - 2
        elif direction == "down-right":
            new_x, new_y = x + 2, y + 2
        elif direction == "up-left":
            new_x, new_y = x - 2, y - 2
        elif direction == "down-left":
            new_x, new_y = x - 2, y + 2

    # Keep AI within screen boundaries
    new_x = max(0, min(screen_width - NEW_WIDTH, new_x))
    new_y = max(0, min(screen_height - NEW_HEIGHT, new_y))

    # Move the AI
    root.geometry(f"+{int(new_x)}+{int(new_y)}")

    # Update cursor tracking
    last_cursor_x, last_cursor_y = current_cursor_x, current_cursor_y
    last_cursor_check_time = current_time

    # Schedule the next movement update
    root.after(50, move_robot)




def speak(audio):
    """Convert text to speech"""
    engine.say(audio)
    engine.runAndWait()
    
def stop_speaking():
    """Stop the speech immediately"""
    engine.stop()

def wishMe():
    """Greet the user based on the time of day"""
    hour = int(datetime.datetime.now().hour)
    if hour < 12:
        speak("Good Morning!")
    elif hour < 17:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    
    speak("How may I assist you?")


def takeCommand():
    """Take voice input from the user and convert it to text"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query.lower()
def calculate_math(query):
    """Perform basic mathematical operations from voice commands."""
    numbers = [int(num) for num in re.findall(r'\d+', query)]
    
    if len(numbers) < 2:
        speak("Please provide two numbers for calculation.")
        return
    
    num1, num2 = numbers[0], numbers[1]

    if "add" in query or "plus" in query or "+" in query:
        result = num1 + num2
        speak(f"The sum of {num1} and {num2} is {result}")
    elif "subtract" in query or "minus" in query or "-" in query  or "subtracted by" in query:
        result = num1 - num2
        speak(f"The difference between {num1} and {num2} is {result}")
    elif "multiply" in query or "times" in query or "*" in query  or "multiplied by" in query or 'x' in query:
        result = num1 * num2
        speak(f"The product of {num1} and {num2} is {result}")
    elif "divide" in query or "divided by" in query or "/" in query:
        if num2 == 0:
            speak("Division by zero is not allowed.")
        else:
            result = num1 / num2
            speak(f"The result of dividing {num1} by {num2} is {result}")
    else:
        speak("I couldn't recognize the operation.")


# Load API key from .env file (Removed os.getenv for direct API key use)
genai.configure(api_key="AIzaSyBUTXskIhQsvGylqCjKGgcUON-ziz3c6Ko")

def create_text_file():
    """Create a text file based on user input"""
    speak("What should be the file name?")
    file_name = takeCommand()

    if file_name == "none":
        speak("File creation canceled.")
        return

    speak("Where should I save the file?")
    location = takeCommand()

    if location == "none":
        speak("File creation canceled.")
        return

    base_path = 'C:\\Users\\pj892\\OneDrive\\Desktop'
    folder_path = base_path if "desktop" in location else os.path.join(base_path, location)

    # Ensure directory exists
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, f"{file_name}.txt")

    speak("What should I write in the file?")
    content = takeCommand()

    if content == "none":
        speak("File creation canceled.")
        return

    try:
        with open(file_path, "w") as file:
            file.write(content)
        speak(f"File {file_name} has been created successfully.")
    except Exception as e:
        speak("I couldn't create the file due to an error.")
        print(e)

def ask_gemini(question):
    """Ask Google Gemini AI a question and return the response"""
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(question)
    return response.text

def quit_screen():
    """Closes the active window by simulating Alt + F4"""
    speak("Closing window")
    time.sleep(1)  # Small delay before action
    pyautogui.hotkey("alt", "f4")

def google_search(query):
    """Opens Google in Chrome, waits for it to load, then types and searches the query"""
    query = query.replace("search", "").replace("on google", "").strip()

    if query:
        speak(f"Searching Google for {query}")

        # Path to Chrome (Update if needed)
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        
        # Open Chrome
        webbrowser.get(chrome_path).open("https://www.google.com")
        
        # Wait for Chrome to open
        time.sleep(2)  # Adjust this based on your system speed

        # Simulate keyboard typing (requires PyAutoGUI)
        pyautogui.write(query, interval=0.1)
        pyautogui.press("enter")

    else:
        speak("I didn't catch that. Please say what to search.")

def search_youtube(query):
    """Opens YouTube in Chrome and searches for the given query"""
    query = query.replace("search", "").replace("on youtube", "").strip()

    if query:
        speak(f"Searching YouTube for {query}")

        # Open YouTube in Chrome
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(chrome_path).open("https://www.youtube.com")

        # Wait for YouTube to load
        time.sleep(5)

        pyautogui.press('/')
        # Type the search query and press Enter
        pyautogui.write(query, interval=0.1)
        pyautogui.press('enter')

    else:
        speak("I didn't catch that. Please say what to search.")

def close_tabs(num_tabs: int = 1) -> None:
    """
    Closes specified number of browser tabs using keyboard shortcuts
    
    Args:
        num_tabs: Number of tabs to close (default=1)
    """
    try:
        # Input validation
        if num_tabs < 1:
            speak("Invalid number of tabs")
            return
            
        speak(f"Closing {num_tabs} {'tab' if num_tabs == 1 else 'tabs'}")
        
        # Small initial delay to prepare
        time.sleep(0.5)
        
        # Close tabs with a small delay between each
        for _ in range(num_tabs):
            pyautogui.hotkey('ctrl', 'w')
            # Brief delay between closes to prevent keyboard buffer overflow
            time.sleep(0.2)
            
        speak("Done")
        
    except Exception as e:
        speak("Error while closing tabs")
        print(f"Error: {e}")


def refresh():
    speak('refreshing')
    time.sleep(1)
    pyautogui.hotkey('f5')

def reload():
    speak('Reloading')
    time.sleep(1)
    pyautogui.hotkey('f5')

def copy():
    pyautogui.hotkey('ctrl','c')
    speak('copied')

def paste():
    pyautogui.hotkey('ctrl','v')
    speak('pasted')

def pause():
    pyautogui.hotkey('space')
   

def take_screenshot():
    """Takes a screenshot and saves it to the Screenshots folder"""
    try:
        # Define the screenshots directory
        screenshots_dir = r"C:\\Users\\pj892\\OneDrive\\Pictures\\Screenshots"
        
        # Create directory if it doesn't exist
        if not os.path.exists(screenshots_dir):
            os.makedirs(screenshots_dir)
            
        # Find next available number
        counter = 1
        while os.path.exists(os.path.join(screenshots_dir, f"Screenshot ({counter}).png")):
            counter += 1
            
        # Full path for the screenshot with extension
        filepath = os.path.join(screenshots_dir, f"Screenshot ({counter}).png")
        
        # Take the screenshot
        screenshot = pyautogui.screenshot()
        
        # Save the screenshot
        screenshot.save(filepath)
        speak("Captured")
        
    except Exception as e:
        speak("Sorry, I couldn't take the screenshot")
        print(f"Error: {e}")

def open_website_or_software(query):
    websites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com",
        "github": "https://www.github.com",
        "quora": "https://www.quora.com",
        "reddit": "https://www.reddit.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://www.twitter.com",
        "linkedin": "https://www.linkedin.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com",
        "wikipedia": "https://www.wikipedia.org",
        "whatsapp": "https://web.whatsapp.com",
        "spotify": "https://open.spotify.com",
    }

    software_paths = {
        "vs code": r"C:\\Users\\pj892\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
        "word": r"C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "notepad": r"C:\Windows\system32\notepad.exe",
        "calculator": r"C:\Windows\System32\calc.exe",
        "command prompt": r"C:\Windows\System32\cmd.exe",
        "paint": r"C:\Windows\System32\mspaint.exe",
        "control panel": r"C:\Windows\System32\control.exe",
        "task manager": r"C:\Windows\System32\Taskmgr.exe",
    }

    query = query.lower()
 
    for site in websites:
        if site in query:
            speak(f"Opening {site.capitalize()}!")
            webbrowser.open(websites[site])
            return

    for software in software_paths:
        if software in query:
            speak(f"Opening {software.capitalize()}!")
            os.startfile(software_paths[software])
            return

    speak("Sorry, I couldn't find that website or software.")

def voice_assistant():
    while True:
        # Start Floating Animation





        query = takeCommand()

        if 'tell me about' in query or "what is" in query:
            speak('Searching Wikipedia...')
            query = query.replace("search", "").replace("tell me about", "").replace("what is", "").strip()
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except wikipedia.exceptions.DisambiguationError:
                speak("There are multiple results. Please be more specific.")
            except wikipedia.exceptions.PageError:
                speak("I couldn't find any information on that.") 

        elif "on google" in query:
            google_search(query)

        elif 'play music' in query:
            speak('Playing music!')
            music_dir = 'C:\\Users\\pj892\\OneDrive\\Desktop\\musics'
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, random.choice(songs)))
            else:
                speak("No music files found in the folder.")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"It's {strTime} right now!")

        elif 'who are you' in query or "what's your name" in query:
            speak("I'm Evelyn, your personal assistant.")

        elif "what's my name" in query:
            speak("Your name is Priyanshu.")

        # elif 'open code' in query:
        #     codepath = "C:\\Users\\pj892\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
        #     speak("Opening VS Code")
        #     os.startfile(codepath)

        elif 'create a folder' in query or 'make a folder' in query:
            speak("What should be the folder name?")
            folder_name = takeCommand()

            if folder_name == "none":
                speak("Folder creation canceled.")
            else:
                base_path = 'C:\\Users\\pj892\\OneDrive\\Desktop'
                folder_path = os.path.join(base_path, folder_name)

                try:
                    os.makedirs(folder_path)
                    speak(f"Folder {folder_name} has been created on your desktop.")
                except FileExistsError:
                    speak("A folder with this name already exists.")

        elif 'create a file' in query or 'make a file' in query or 'save my words' in query:
            create_text_file()

        elif 'ask gemini' in query or 'ask ai' in query:
            speak("What would you like to ask?")
            user_question = takeCommand()

            if user_question == "none":
                speak("I couldn't understand the question.")
            else:
                speak("Thinking...")
                ai_response = ask_gemini(user_question)
                print("Gemini AI:", ai_response)
                speak(ai_response)

        elif 'stop speaking' in query or 'be quiet' in query:
            stop_speaking()
            speak("Okay, I will stop now.")

        elif 'end' in query:
            speak("Goodbye! Hope to see you again.")
            exit()

        elif 'what can you do' in query:
            speak("I can perform various tasks like searching Wikipedia, opening websites, playing music, checking the time, creating folders, creating text files, and answering your questions using AI.")
        
        elif 'quit screen' in query or 'close window' in query:
             quit_screen()

        elif 'on youtube' in query:
            search_youtube(query)

        # elif 'tab' in query:
        #     close_tab() 

        elif 'refresh' in query:
            refresh()

        elif 'reload' in query:
            reload()

        elif 'copy' in query:
            copy()

        elif 'paste' in query:
            paste()

        elif "add" in query or "subtract" in query or "multiply" in query or "divide" in query or "+" in query or "plus" in query or "-" in query or "minus" in query or "divided by" in query or "/" in query or "multiplied by" in query or "*" in query or 'x' in query:
            calculate_math(query)
        
        elif 'minimize' in query or 'minimise' in query:
            pyautogui.hotkey('win', 'd')

        elif 'take screenshot' in query or 'capture screen' in query or 'take a screenshot' in query:
            take_screenshot()
        
        elif "open" in query:
            open_website_or_software(query.replace("open", "").strip())


        elif 'close tab' in query or 'close tabs' in query:
             try:
        # Extract number from command if present
                 words = query.split()
                 num = next((int(word) for word in words if word.isdigit()), 1)
                 close_tabs(num)
             except Exception:
                      close_tabs()

        elif 'pause' in query or 'stop' in query:
            pause() 


if __name__ == "__main__":
 wishMe()
move_robot()
# Run voice assistant in a separate thread
threading.Thread(target=voice_assistant, daemon=True).start()
root.mainloop()