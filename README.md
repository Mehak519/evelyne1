import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import sympy as sp
import math

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Change voice if needed

def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Sir!")
    elif hour >= 12 and hour < 17:
        speak("Good Afternoon Sir!") 
    else:
        speak("Good Evening Sir!")
    
    speak("How may I help you?")

def takeCommand():
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
    return query

def solve_math(expression):
    try:
        expression = expression.replace("plus", "+").replace("minus", "-")
        expression = expression.replace("multiply by", "*").replace("times", "*")
        expression = expression.replace("divide by", "/").replace("over", "/")
        expression = expression.replace("power of", "**")
        result = eval(expression, {"__builtins__": {}}, {"sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log, "sqrt": math.sqrt, "pi": math.pi, "e": math.e})
        return f"The answer is {result}" 
    except Exception as e:
        return "I couldn't solve the problem. Please try again."

if __name__ == "__main__":
    wishMe()
    while True:
        query = takeCommand().lower()

        if 'search' in query or 'tell me about' in query or "what is" in query:
            speak('Searching')
            query = query.replace("search", "").replace("tell me about", "").replace("what is", "").strip()
            try:
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                print(results)
                speak(results)
            except wikipedia.exceptions.DisambiguationError as e:
                speak("There are multiple results. Please be more specific.")
                print(e)
            except wikipedia.exceptions.PageError:
                speak("I couldn't find any information on that.")    

        elif 'open youtube' in query:
            speak('Opening YouTube!')
            webbrowser.open("youtube.com")
        
        elif 'open google' in query:
            speak('Opening Google!')
            webbrowser.open("google.com")

        elif 'play music' in query:
            speak('Sure!')
            music_dir = 'C:\\Users\\pj892\\OneDrive\\Desktop\\musics'
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, random.choice(songs)))
            else:
                speak("No music files found in the folder.")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(strTime)
            speak(f"It's {strTime} right now!")

        elif 'who are you' in query or "hu r u" in query:
            speak("I'm your personal assistant Zira")
        elif "what's your name" in query:
            speak("I'm Zira, your own personal assistant.")
        elif "what's my name" in query:
            speak("Your name is Priyanshu.")
        elif "nice" in query:
            speak("Glad you like it!")
        elif "good" in query:
            speak("Thank you!")
        elif "what else can you do" in query:
            speak("I'm still learning, sir!")

        elif 'open code' in query:
            codepath = "C:\\Users\\pj892\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            speak("Opening VS Code")
            os.startfile(codepath)

        elif 'create folder' in query or 'make a folder' in query:
            speak("What should be the folder name?")
            folder_name = takeCommand().lower()

            if folder_name == "none":
                speak("Folder creation canceled.")
            else:
                desktop_path = 'C:\\Users\\pj892\\OneDrive\\Desktop'
                os.chdir(desktop_path)
                folder_path = os.path.join(desktop_path, folder_name)

                try:
                    os.makedirs(folder_path)
                    speak(f"Folder {folder_name} has been created on your desktop.")
                except FileExistsError:
                    speak("A folder with this name already exists on your desktop.")

        elif 'quit' in query or 'end' in query or "stop" in query:
            speak("Goodbye! Hope to see you again, sir!")
            exit()

        elif 'what can you do' in query:
            speak("I'm a basic AI. I can perform various tasks like searching Wikipedia, opening websites, playing music, checking the time, and even creating folders.")

        elif 'can you calculate' in query or 'can you perform calculations' in query:
            speak("Sure, please say the mathematical expression.")
            expression = takeCommand().lower()
            if expression != "none":
                answer = solve_math(expression)
                speak(answer)
                print(answer)
