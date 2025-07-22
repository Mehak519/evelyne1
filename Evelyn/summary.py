import google.generativeai as genai
import pyperclip
import pyttsx3
import time

# Configure your Gemini API key (replace 'YOUR_API_KEY' with an actual key)
genai.configure(api_key="AIzaSyBUTXskIhQsvGylqCjKGgcUON-ziz3c6Ko")

engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def ask_gemini(question):
    """Ask Google Gemini AI a question and return the response"""
    model = genai.GenerativeModel("gemini-1.5-pro")  # Use the latest available model
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(question)
    return response.text.strip() if response else "Error: No response from Gemini."

def summarize_with_gemini(text):
    """Summarizes given text using Google Gemini API"""
    prompt = f"Summarize the following text concisely:\n{text}"
    return ask_gemini(prompt)

def monitor_clipboard():
    """Continuously monitor clipboard for text and summarize it using Gemini"""
    last_clipboard = ""

    while True:
        time.sleep(2)  # Check clipboard every 2 seconds
        selected_text = pyperclip.paste()

        if selected_text and selected_text != last_clipboard:
            last_clipboard = selected_text
            speak("Text detected. Summarizing using Gemini...")

            # Get summary from Gemini
            summary = summarize_with_gemini(selected_text)

            if len(summary) > 100:
                with open("summary.txt", "w", encoding="utf-8") as file:
                    file.write(summary)
                speak("The summary is too long. It has been saved in 'summary.txt'.")
            else:
                print("Summary:", summary)
                speak(summary)

if __name__ == "__main__":
    speak("Copy the text you want summarized.")
    monitor_clipboard()  # Start monitoring clipboard