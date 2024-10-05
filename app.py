from flask import Flask, render_template, request, jsonify
import json
import random
import re
import pyttsx3

import os
from gtts import gTTS
import time

app = Flask(__name__)

# Load responses from the provided JSON data
with open('responses.json', 'r') as file:
    responses_data = json.load(file)
    tags_and_responses = responses_data.get('tags', [])

# Load intents from the provided JSON data
with open('intents.json', 'r') as file:
    intents_data = json.load(file)
    intents = intents_data.get('intents', [])

def get_response(user_input):
    user_input = user_input.lower()


    # Check tag-based responses
    for tag_data in tags_and_responses:
        if tag_data["tag"] in user_input:
            return random.choice(tag_data["responses"])

    # Check intent-based responses
    for intent in intents:
        patterns = intent.get('patterns', [])  # Use get() to handle missing 'patterns' key
        for pattern in patterns:
            if re.search(pattern.lower(), user_input):
                return random.choice(intent.get('responses', []))

    return "I'm not sure how to respond to that. Can you rephrase or provide more details?"

@app.route("/")
def index():
    return render_template('chat.html')

@app.route("/get", methods=["POST"])
def chat():
    user_input = request.form["msg"]
    response = get_response(user_input)
    
    voice_path = generate_voice_response(response)

    return jsonify({'text_response': response, 'voice_response': voice_path})

def generate_voice_response(text_response):
    timestamp = int(time.time())
    voice_path = f'static/voice_response_{timestamp}.mp3'
    voice_response = gTTS(text=text_response, lang='en', slow=False)
    voice_response.save(voice_path)

    # Play the audio response

    engine = pyttsx3.init()
    engine.say(text_response)
    engine.runAndWait()
    engine.stop()

    # Delete the audio file after playing
    os.remove(voice_path)

    return voice_path

if __name__ == '__main__':
    app.run(debug=True)
