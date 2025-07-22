import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import requests

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Adjust voice if needed

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
    
    speak("How may I assist you?")

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

def create_text_file():
    speak("What should be the file name?")
    file_name = takeCommand().lower()
    
    if file_name == "none":
        speak("File creation canceled.")
        return
    
    speak("Where should I save the file?")
    location = takeCommand().lower() 

    if location == "none":
        speak("File creation canceled.")
        return 
    
    if "desktop" in location:
       folder_path = 'C:\\Users\\pj892\\OneDrive\\Desktop'
    else:
        b_path = 'C:\\Users\\pj892\\OneDrive\\Desktop'
        folder_path = os.path.join(b_path, location)

    file_path = os.path.join(folder_path, f"{file_name}.txt")

    speak("What should I write in the file?")
    content = takeCommand()

    if content == "none":
        speak("File creation canceled.")
        return

    try:
        with open(file_path, "w") as file:
            file.write(content)
        speak(f"File {file_name} has been created")
    except Exception as e:
        speak("I couldn't create the file due to an error.")
        print(e)

# Function to get weather information
def get_weather(city):
    api_key = "173093aa33d79bac3822ffed334b8ccf"  # Replace with your OpenWeather API key
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(complete_url)
        data = response.json()
        
        if data["cod"] != "404":
            main = data["main"]
            weather = data["weather"][0]
            
            temp = main["temp"]
            pressure = main["pressure"]
            humidity = main["humidity"]
            description = weather["description"]
            
            weather_report = f"Weather in {city}: {description}. Temperature: {temp}°C, Humidity: {humidity}%, Pressure: {pressure} hPa."
            return weather_report
        else:
            return "City not found!"
    except Exception as e:
        return "Sorry, I couldn't fetch the weather details."

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
            music_dir = 'C:\\Users\\Acer\\OneDrive\\Desktop\\musics'
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
            speak("I'm your personal assistant Evelyn")
        elif "what's your name" in query:
            speak("I'm Evelyn, your personal assistant.")
        elif "what's my name" in query:
            speak("Your name is Omprakash.")
        elif "nice" in query:
            speak("Glad you like it!")
        elif "good" in query:
            speak("Thank you!")
        elif "what else can you do" in query:
            speak("I'm still learning, sir!")

        elif 'open code' in query:
            codepath = "C:\\Users\\Acer\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            speak("Opening VS Code")
            os.startfile(codepath)

        elif 'create a folder' in query or 'make a folder' in query:
            speak("What should be the folder name?")
            folder_name = takeCommand().lower()

            if folder_name == "none":
                speak("Folder creation canceled.")
            else:
                desktop_path = 'C:\\Users\\Acer\\Desktop'
                folder_path = os.path.join(desktop_path, folder_name)

                try:
                    os.makedirs(folder_path)
                    speak(f"Folder {folder_name} has been created on your desktop.")
                except FileExistsError:
                    speak("A folder with this name already exists on your desktop.")

        elif 'create a file' in query or 'make a file' in query or 'save my words' in query:
            create_text_file()

        elif 'quit' in query or 'end' in query or "stop" in query:
            speak("Goodbye! Hope to see you again.")
            exit()

        elif 'weather in' in query:
            city = query.replace("weather in", "").strip()
            speak(f"Checking weather in {city}...")
            weather_info = get_weather(city)
            speak(weather_info)
            print(weather_info)

        elif 'what can you do' in query:
            speak("I can perform various tasks like searching Wikipedia, opening websites, playing music, checking the time, creating folders, creating text files, and even checking the weather.")
