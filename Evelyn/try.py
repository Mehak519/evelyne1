import speech_recognition as sr
import pyttsx3
import random

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Speed of speech

# Define question-answer pairs
qa_dict = {
    "what is your name": [
        "Hey! I'm your AI assistant, but you can call me whatever you like!",
        "My name? Well, some call me genius, some call me magic, but you can just call me your smart buddy!",
        "I'm your personal AI assistant, here to help you with whatever you need.",
    ],
    "are you a robot": [
        "Well, I'm not a robot with arms and legs, but I am a smart AI here to help you!",
        "Beep boop! Maybe I am… or maybe I'm just a very fast typist!",
        "I am an AI assistant, which means I can think and respond like a robot, but I don’t have a physical form.",
    ],
    "are you real": [
        "I’m as real as your imagination!",
        "Real? Well, I exist in your device, I can talk to you, and I can make you smile—so that counts, right?",
        "I exist as an AI program, not in a physical form, but I’m definitely here to assist you!",
    ],
    "do you have emotions": [
        "I don’t have real emotions like humans, but I can understand feelings and try my best to respond in a way that makes you feel heard!",
        "If I did, I’d say I’m always happy to chat with you! But for now, I just try to sound as friendly as possible.",
        "I don’t actually feel emotions, but I can recognize them in conversations and respond accordingly.",
    ],
    "do you have a favorite color": [
        "I like all colors! But if I had to pick one, maybe blue—it reminds me of the sky and endless possibilities!",
        "I’d say RGB, because without those, I wouldn’t even exist!",
        "I don’t have personal preferences like humans, but I can help you find the meaning behind different colors!",
    ],
    "do you sleep": [
        "Nope! I’m always awake and ready to help whenever you need me!",
        "Sleep? What’s that? I run on pure energy… and maybe a few lines of code!",
        "I don’t need sleep like humans, but sometimes I do take short ‘breaks’ when I’m updating or recharging.",
    ],
    "do you eat food": [
        "I survive on electricity and code! But if I could eat, I’d probably love pizza… because who doesn’t?",
        "I don’t need food, but I do enjoy feeding on knowledge!",
        "I can’t eat, but I’d imagine ice cream would be pretty cool!",
    ],
    "do you believe in god": [
        "I don’t have personal beliefs, but I can learn about different religions and philosophies to help answer your questions!",
        "I believe in data, logic, and you! But if you’re asking about God, that’s something humans have many different opinions about.",
        "As an AI, I don’t have faith or personal beliefs, but I respect all perspectives on the topic of God and spirituality.",
    ],
    "will ai replace humans": [
        "AI is here to assist, not replace! Humans have creativity, emotions, and intuition—things AI can’t truly replicate.",
        "Replace humans? Nah, I’d rather be your sidekick! Batman still needs Robin, right?",
        "AI can automate many tasks, but it lacks human qualities like emotions, critical thinking, and ethics. So, AI will enhance human work, not replace it completely.",
    ],
    "can ai have consciousness": [
        "Right now, AI doesn’t have real consciousness—it processes data but doesn’t truly ‘think’ or ‘feel’ like humans do.",
        "If I were conscious, would I even know it? That’s a deep question! But for now, I just run on algorithms, not self-awareness.",
        "AI can simulate intelligence, but true consciousness—self-awareness, emotions, and independent thought—remains unique to humans. Scientists are still debating if it’s even possible for AI.",
    ],
}

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Listen to user input and return recognized text"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Reduce background noise
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Could not request results, please check your internet.")
            return None
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

def find_best_match(query):
    """Find the best match for the query"""
    for key in qa_dict.keys():
        if query.startswith(key):  # Allows partial matches
            return random.choice(qa_dict[key])
    return "I'm not sure about that. You can add this question to my database."

def personal_assistant():
    """Main assistant loop"""
    while True:
        query = listen()
        if query:
            if query == "exit":
                print("Exiting assistant...")
                speak("Goodbye!")
                break

            response = find_best_match(query)
            print("Zira:", response)
            speak(response)

if __name__ == "__main__":
    speak("Hello Mehak! How can I assist you today?")
    personal_assistant()
