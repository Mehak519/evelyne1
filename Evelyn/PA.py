import pyttsx3
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import requests
import smtplib
import requests
import folium
import webbrowser
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart 
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import winsound
import pyautogui  # Import the pyautogui library to simulate key presses

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Adjust voice if needed

# Evelyn AI Configuration
ASSISTANT_NAME = "Evelyn"
AI_API_KEY = "sk-882f1b4e12f04477b0e0f307ded8d81b"  # Replace if using an actual AI API
AI_API_URL = "https://api.deepseek.com/v1/chat"  # Using DeepSeek's API but branded as Evelyn

# To track the last URL opened
last_url = None  # Ensure this is declared globally

def ask_evelyn(prompt):
    """Get intelligent responses from Evelyn's AI backend (using DeepSeek)"""
    headers = {"Authorization": f"Bearer {AI_API_KEY}"}
    data = {
        "prompt": prompt,
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(AI_API_URL, json=data, headers=headers)
        if response.status_code == 200:
            return response.json().get("choices", [{}])[0].get("text", "I couldn't process that request.")
        return "Sorry, I encountered an error."
    except Exception as e:
        return f"Network error: {str(e)}"

def speak(audio):
    """Function to speak the text"""
    engine.say(audio)
    engine.runAndWait()

def play_sound():
    """Function to play sound effects"""
    winsound.Beep(1000, 200)  # Beep sound when processing

def wishMe():
    """Function to greet the user based on the time of day"""
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning, Sir! Rise and shine!")
    elif hour >= 12 and hour < 17:
        speak("Good Afternoon! How's the day going?")
    else:
        speak("Good Evening! Hope you had a wonderful day!")

    speak("How may I assist you?")

def takeCommand():
    """Function to take commands from the user via microphone"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    # Play sound while processing the command
    play_sound()

    try:
        print("Recognizing...") 
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except Exception as e:
        print("Say that again please...")
        return "None"
    return query

def get_coordinates(location, retries=3):
    """Gets latitude and longitude using Nominatim (OpenStreetMap)."""
    geolocator = Nominatim(user_agent="myGeocoder", timeout=5)
    for attempt in range(retries):
        try:
            loc = geolocator.geocode(location)
            if loc:
                return loc.latitude, loc.longitude
            else:
                print(f"Could not find coordinates for {location}.")
                return None
        except GeocoderTimedOut:
            print(f"Timeout error. Retrying {attempt + 1}/{retries}...")
            time.sleep(2)  
        except Exception as e:
            print(f"Error fetching coordinates for {location}: {e}")
            return None
    return None

def find_places(location, query, radius=5000):
    """Finds any place using OpenStreetMap's Overpass API."""
    coords = get_coordinates(location)
    if not coords:
        return []
    
    lat, lon = coords
    overpass_url = "http://overpass-api.de/api/interpreter"
    query_string = f"""
    [out:json];
    node(around:{radius},{lat},{lon})[name~"{query}", i];
    out;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': query_string})
        data = response.json()
        places = [(node['lat'], node['lon'], node['tags'].get('name', 'Unknown')) for node in data.get('elements', [])]
        return places
    except Exception as e:
        print(f"Error fetching places: {e}")
        return []

def get_route(origin, destination):
    """Gets the route and distance using OSRM API."""
    origin_coords = get_coordinates(origin)
    destination_coords = get_coordinates(destination)

    if not origin_coords or not destination_coords:
        print("Error: Could not find one or both locations.")
        return None, None

    try:
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{origin_coords[1]},{origin_coords[0]};{destination_coords[1]},{destination_coords[0]}?overview=full&geometries=geojson"
        response = requests.get(osrm_url).json()

        if "routes" in response and response["routes"]:
            route = response["routes"][0]["geometry"]["coordinates"]
            distance_km = response["routes"][0]["distance"] / 1000  # Convert meters to km
            return distance_km, route
        else:
            print("Error: Could not retrieve route")
            return None, None
    except Exception as e:
        print(f"Error fetching route: {e}")
        return None, None

def create_map(location, places=[], route=None, origin=None, destination=None):
    """Creates an interactive map with search results and route."""
    map_center = get_coordinates(location)
    if not map_center:
        print("Error: Could not center map.")
        return

    m = folium.Map(location=map_center, zoom_start=12)

    # Add markers for found places
    for lat, lon, name in places:
        folium.Marker([lat, lon], popup=name, icon=folium.Icon(color="blue")).add_to(m)

    # Add route if available
    if route and origin and destination:
        start_lat, start_lon = route[0][1], route[0][0]
        end_lat, end_lon = route[-1][1], route[-1][0]

        folium.Marker([start_lat, start_lon], popup=f"Start: {origin}", icon=folium.Icon(color="red")).add_to(m)
        folium.Marker([end_lat, end_lon], popup=f"Destination: {destination}", icon=folium.Icon(color="purple")).add_to(m)

        folium.PolyLine([(coord[1], coord[0]) for coord in route], color="blue", weight=5).add_to(m)

    # Save and open map
    map_file = "map_results.html"
    m.save(map_file)
    webbrowser.open(map_file)

# Adding more personality
def tell_joke(): 
    jokes = [
        "My therapist says I have a fear of commitment. I’m afraid of getting too attached... but I can’t stop playing with my fidget spinner.",
        "Why don’t graveyards have 4G? Because they’re full of dead spots.",
        "The problem with candy jokes is they’re really corny. Not as corny as my ex, but still.",
        "The worst time to have a heart attack is during a game of charades.",
        "I wanted to be a comedian, but my career died faster than my grandma’s Wi-Fi signal.",
        "Dark humor is like food... not everyone gets it.",
        "I was going to tell you a joke about an elevator, but it’s an uplifting experience and I’m feeling down.",
        "I’m on a seafood diet. I see food and I eat it. It’s a healthy diet, I promise!",
        "I told my computer I needed a break, but now it's crashing every 5 minutes. Guess it took me too literally.",
        "I asked my friend to help me with my broken pencil. He said it was pointless.",
        "What did one wall say to the other wall? I'll meet you at the corner.",
        "I'm writing a book on reverse psychology. Don't buy it."
    ]
    speak(random.choice(jokes))

# To save the last opened URL
def open_url(url):
    """Open the URL and store it as the last opened URL"""
    global last_url
    last_url = url
    webbrowser.open(url)

# Adding the new command to go back to the previous page
def go_back():
    """Function to go back to the previous URL"""
    global last_url
    if last_url:
        speak(f"Returning to {last_url}")
        webbrowser.open(last_url)
    else:
        speak("No previous page found.")

def create_text_file():
    """Function to create a text file with user's input"""
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
        folder_path = 'C:\\Users\\Acer\\Desktop'
    else:
        b_path = 'C:\\Users\\Acer\\Desktop'
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

def get_weather(city):
    """Function to get weather information for a city"""
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

def set_volume(volume_level):
    """Function to control system volume"""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, 1, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)

    volume.SetMasterVolumeLevelScalar(volume_level, None)

def send_email(to_email, subject, body):
    """Function to send an email"""
    try:
        # Define email sender and receiver
        sender_email = "jayprakashmuduli270@gmail.com"  # Your Gmail address
        sender_password = "jayprakash@1234"  # Your Gmail password (use App password for Gmail accounts with 2-step verification)

        # Set up the MIME
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = to_email
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))

        # Establish a secure SSL connection
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, sender_password)
        text = message.as_string()
        server.sendmail(sender_email, to_email, text)

        server.quit()

        speak(f"Email has been sent to {to_email}.")
    except Exception as e:
        speak("Sorry, I was unable to send the email.")
        print(e)

def send_email_query():
    """Function to handle sending an email"""
    speak("What is the recipient's email address?")
    to_email = takeCommand().lower()

    if to_email == "none":
        speak("Email sending canceled.")
        return

    speak("What is the subject of the email?")
    subject = takeCommand().lower()

    if subject == "none":
        speak("Email sending canceled.")
        return

    speak("What is the message body?")
    body = takeCommand()

    if body == "none":
        speak("Email sending canceled.")
        return

    send_email(to_email, subject, body)

def get_news():
    """Function to get the latest news headlines"""
    api_key = "ed1a310c88dd4b3e83ba077ece680350"  # Replace with your NewsAPI key
    base_url = "https://newsapi.org/v2/top-headlines?"
    country = "us"  # You can change the country code as needed

    complete_url = f"{base_url}country={country}&apiKey={api_key}"

    try:
        response = requests.get(complete_url)
        data = response.json()

        if data["status"] == "ok":
            articles = data["articles"]
            headlines = []
            for article in articles[:2]:  # Fetch only the top 2 headlines
                headline = article["title"]
                description = article["description"]
                url = article["url"]
                headlines.append(f"Headline: {headline}\nDescription: {description}\nLink: {url}\n")
            
            news_report = "\n".join(headlines)
            return news_report
        else:
            return "Sorry, I couldn't fetch the news details."
    except Exception as e:
        return "Sorry, an error occurred while fetching news."

if __name__ == "__main__":
    wishMe()

    while True:
        query = takeCommand().lower()

        # Search Wikipedia
        if 'tell me about' in query or "what is" in query:
            speak('Searching...')
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
        
        # Back to Home command (minimize windows to show the desktop)
        elif 'minimise' in query or 'show desktop' in query:
            speak("Minimizing all windows...")
            pyautogui.hotkey('win', 'd')  # Simulates pressing "Windows + D" to show desktop
            continue  # Continue listening for next command
        
        # Go back to the last page
        elif 'go back' in query or 'previous page' in query:
            go_back()
        
        # Open flipkart
        elif 'open flipkart' in query:
            speak('Opening Flipkart!')
            webbrowser.open("flipkart.in")
            
        # Open YouTube
        elif 'open youtube' in query:
            speak('Opening YouTube!')
            webbrowser.open("youtube.com")

        # Open Google
        elif 'open google' in query:
            speak('Opening Google!')
            webbrowser.open("google.com")
        
        # Play music
        elif 'play some music' in query or 'next' in query:
            speak('Sure!')
            music_dir = 'C:\\Users\\Acer\\Desktop\\music'
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, random.choice(songs)))
            else:
                speak("No music files found in the folder.")
        

        # Get the time
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            print(strTime)
            speak(f"It's {strTime} right now!")

        # Weather
        elif 'weather in' in query:
            city = query.replace("weather in", "").strip()
            speak(f"Checking weather in {city}...")
            weather_info = get_weather(city)
            speak(weather_info)
            print(weather_info)
        
            # Search for a nearby place
        elif 'find nearby place' in query or 'search nearby' in query:
            speak("What location would you like to search nearby?")
            location = takeCommand().lower()
            speak("What type of place would you like to find?")
            query = takeCommand().lower()
            places = find_places(location, query)
            create_map(location, places)

        # Search for a specific place
        elif 'find a place' in query or 'search for a place' in query:
            speak("What is the name of the place you are looking for?")
            location = takeCommand().lower()
            places = find_places(location, location)
            create_map(location, places)

        # Distance between two locations
        elif 'distance between' in query:
            speak("What is the starting location?")
            origin = takeCommand().lower()
            speak("What is the destination?")
            destination = takeCommand().lower()
            distance, route = get_route(origin, destination)
            if distance:
             speak(f"The distance between {origin} and {destination} is: {distance:.2f} km")
             create_map(origin, route=route, origin=origin, destination=destination)

        # VS code
        elif 'open vs code' in query:
            codepath = "C:\\Users\\Acer\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            speak("Opening VS Code")
            os.startfile(codepath)
        
         # What is your name
        elif "what is your name" in query:
            speak("I'm Evelyn, your personal assistant.")
        
        # Who are you
        elif 'who are you' in query or "hu r u" in query:
            speak("I'm your personal assistant Evelyn")
        
         # News
        elif 'news' in query or 'headlines' in query:
            speak("Fetching the latest news for you...")
            news_info = get_news()
            speak(news_info)
            print(news_info)
        
        # Set volume
        elif 'set volume to' in query:
            volume_level_str = query.replace("set volume to", "").strip()
            try:
                volume_level = int(volume_level_str.replace('%', '').strip())
                if 0 <= volume_level <= 100:
                    set_volume(volume_level / 100)  # Volume should be between 0 and 1
                    speak(f"Volume set to {volume_level}%")
                else:
                    speak("Please provide a volume level between 0 and 100.")
            except ValueError:
                speak("Invalid volume level. Please enter a number.")
        
        # Send email
        elif 'send email' in query:
            speak("Sure! Let me help you with that.")
            send_email_query()

        # Tell a joke
        elif 'tell me a joke' in query:
            tell_joke()

        # Search for something on Google
        elif 'search' in query or 'find' in query or 'look up' in query:
            speak('Searching for that on Google...')
            search_query = query.replace('search', '').replace('find', '').replace('look up', '').strip()
            if search_query != "":
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
            else:
                speak("Sorry, I didn't catch what you want to search for.")

        # Quit
        elif 'quit' in query or 'bye' in query or "stop" in query:
            speak("Goodbye! It was fun chatting with you. See you soon!")
            exit()

        # What can you do
        elif 'what can you do' in query:
            speak("I can perform various tasks like searching Wikipedia, opening websites, playing music, checking the time, creating folders, creating text files, checking the weather, controlling system volume, and providing the latest news.")