import pyperclip
import pyttsx3
import time
import asyncio
from googletrans import Translator

engine = pyttsx3.init()
translator = Translator()

TARGET_LANGUAGE = "hi"  # Change this to your desired language (e.g., 'fr' for French, 'es' for Spanish)

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

async def translate_text(text, target_lang):
    """Asynchronously translate English text into the selected language."""
    try:
        translation = await translator.translate(text, dest=target_lang)
        return translation.text
    except Exception as e:
        return f"Error: {e}"

def monitor_clipboard():
    """Continuously monitor clipboard for text and translate it."""
    last_clipboard = ""

    while True:
        time.sleep(2)  # Check clipboard every 2 seconds
        copied_text = pyperclip.paste()

        if copied_text and copied_text != last_clipboard:
            last_clipboard = copied_text
            speak("Text detected. Translating...")

            # Use asyncio to run the async function
            translated_text = asyncio.run(translate_text(copied_text, TARGET_LANGUAGE))

            if len(translated_text) > 100:
                with open("translation.txt", "w", encoding="utf-8") as file:
                    file.write(translated_text)
                speak("The translation is too long. It has been saved in 'translation.txt'.")
            else:
                print(f"Translation ({TARGET_LANGUAGE}):", translated_text)
                speak(translated_text)

if __name__ == "__main__":
    speak("Copy the text you want to translate.")
    monitor_clipboard()
