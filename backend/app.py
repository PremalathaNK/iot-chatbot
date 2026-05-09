from flask import Flask, render_template
from flask import request, jsonify

import requests
import random
import re

from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# =========================================
# ESP32 IP
# =========================================

ESP32_IP = "http://10.61.103.174"

# =========================================
# LOAD AI MODEL
# =========================================

print("Loading AI Model...")

model = SentenceTransformer(
    'all-MiniLM-L6-v2'
)

print("AI Model Loaded")

# =========================================
# INTENT TRAINING DATA
# =========================================

intent_examples = {

    "light_on": [

        "turn on light",
        "lights on",
        "make room bright",
        "its dark",
        "i cannot see",
        "too dark here",
        "brighten the room",
        "switch on lights",
        "need more light",
        "room is dark",
        "enable lights"
    ],

    "light_off": [

        "turn off light",
        "lights off",
        "good night",
        "make room dark",
        "dim the room",
        "i want sleep",
        "switch off lights",
        "disable lights",
        "too bright",
        "reduce brightness",
        "room is bright"
    ],

    "play_music": [

        "play music",
        "i am bored",
        "entertain me",
        "play melody",
        "music please",
        "play song",
        "i want music",
        "make some sound",
        "fun mode"
    ],

    "disco_mode": [

        "disco",
        "party mode",
        "dance mode",
        "club lights",
        "celebration mode",
        "lets dance",
        "party time"
    ],

    "rgb_red": [

        "red light",
        "make room red",
        "red ambience",
        "red mood"
    ],

    "rgb_blue": [

        "blue light",
        "make room blue",
        "blue ambience",
        "cool blue"
    ],

    "rgb_green": [

        "green light",
        "make room green"
    ],

    "rgb_off": [

        "turn off rgb",
        "disable rgb",
        "rgb off",
        "remove ambient lights"
    ],

    "buzzer_on": [

        "turn on alarm",
        "alert me",
        "activate buzzer",
        "danger alert",
        "wake me up",
        "start alarm"
    ],

    "buzzer_off": [

        "turn off alarm",
        "disable buzzer",
        "stop alert",
        "alarm off"
    ],

    "smart_mode_on": [

        "smart mode",
        "automatic lighting",
        "auto mode",
        "enable smart mode"
    ],

    "smart_mode_off": [

        "disable smart mode",
        "turn off smart mode",
        "stop smart lighting"
    ],

    "temperature": [

        "temperature",
        "how hot is it",
        "current temperature",
        "room temperature"
    ],

    "ldr": [

        "ldr value",
        "light level",
        "brightness level"
    ]
}

# =========================================
# RESPONSES
# =========================================

responses = {

    "light_on": [

        "Lights turned on 💡",
        "Brightness increased 🌟",
        "Room illuminated successfully ✨"
    ],

    "light_off": [

        "Lights turned off 🌑",
        "Room dimmed successfully 😴",
        "Good night mode activated 🌙"
    ],

    "play_music": [

        "Playing melody 🎵",
        "Enjoy the music 🎶",
        "Starting entertainment mode ✨"
    ],

    "disco_mode": [

        "Disco mode activated 🕺",
        "Party lights enabled 🎉",
        "Dance mode started 💃"
    ],

    "rgb_red": [

        "Red ambience enabled ❤️",
        "Room glowing red 🔴"
    ],

    "rgb_blue": [

        "Blue ambience enabled 💙",
        "Cool blue lighting activated 🔵"
    ],

    "rgb_green": [

        "Green ambience activated 💚"
    ],

    "rgb_off": [

        "Ambient lights turned off ⚫"
    ],

    "buzzer_on": [

        "Alarm activated 🚨",
        "Alert system enabled ⚠️"
    ],

    "buzzer_off": [

        "Alarm disabled 🔕"
    ],

    "smart_mode_on": [

        "Smart lighting enabled 🤖"
    ],

    "smart_mode_off": [

        "Smart mode disabled 🛑"
    ]
}

# =========================================
# FUNCTION MAP
# =========================================

FUNCTIONS = {

    "light_on": "lighton",
    "light_off": "lightoff",

    "play_music": "melody",

    "disco_mode": "disco",

    "rgb_red": "rgbred",
    "rgb_blue": "rgbblue",
    "rgb_green": "rgbgreen",
    "rgb_off": "rgboff",

    "buzzer_on": "buzzeron",
    "buzzer_off": "buzzeroff",

    "smart_mode_on": "smartmode",
    "smart_mode_off": "smartmodeoff",

    "temperature": "temperature",

    "ldr": "ldr"
}

# =========================================
# CREATE EMBEDDINGS
# =========================================

all_sentences = []
all_intents = []

for intent, examples in intent_examples.items():

    for sentence in examples:

        all_sentences.append(sentence)

        all_intents.append(intent)

sentence_embeddings = model.encode(
    all_sentences
)

# =========================================
# TEXT CLEANER
# =========================================

def clean_text(text):

    text = text.lower()

    fixes = {

        "turn of": "turn off",
        "trun": "turn",
        "ligth": "light",
        "alaram": "alarm",
        "musci": "music"
    }

    for wrong, correct in fixes.items():

        text = text.replace(
            wrong,
            correct
        )

    return text

# =========================================
# SEND COMMAND
# =========================================

def send_command(command):

    try:

        response = requests.get(

            f"{ESP32_IP}/{command}",

            timeout=5
        )

        return response.text

    except:

        return None

# =========================================
# DETECT INTENT
# =========================================

def detect_intent(user_message):

    msg = clean_text(user_message)

    # =====================================
    # RULE ENGINE
    # =====================================

    # DISCO

    if any(x in msg for x in [

        "disco",
        "party",
        "dance",
        "club"
    ]):

        return "disco_mode"

    # RGB COLORS

    if "red" in msg:

        if "off" in msg:

            return "rgb_off"

        return "rgb_red"

    if "blue" in msg:

        if "off" in msg:

            return "rgb_off"

        return "rgb_blue"

    if "green" in msg:

        return "rgb_green"

    # SMART MODE

    if "smart mode" in msg:

        if "off" in msg:

            return "smart_mode_off"

        return "smart_mode_on"

    # ALARM

    if any(x in msg for x in [

        "alarm",
        "alert",
        "buzzer"
    ]):

        if any(x in msg for x in [

            "off",
            "stop",
            "disable"
        ]):

            return "buzzer_off"

        return "buzzer_on"

    # LIGHTS

    if any(x in msg for x in [

        "light",
        "lights",
        "bright",
        "dark"
    ]):

        if any(x in msg for x in [

            "off",
            "dark",
            "sleep",
            "night",
            "dim",
            "dull"
        ]):

            return "light_off"

        return "light_on"

    # MUSIC

    if any(x in msg for x in [

        "music",
        "melody",
        "song",
        "bored",
        "entertain"
    ]):

        return "play_music"

    # TEMPERATURE

    if "temperature" in msg:

        return "temperature"

    # LDR

    if "ldr" in msg:

        return "ldr"

    # =====================================
    # AI SEMANTIC FALLBACK
    # =====================================

    user_embedding = model.encode([msg])

    similarities = cosine_similarity(

        user_embedding,

        sentence_embeddings
    )

    best_index = similarities.argmax()

    confidence = similarities[0][best_index]

    detected_intent = all_intents[best_index]

    print("\nCONFIDENCE:", confidence)

    print("INTENT:", detected_intent)

    if confidence < 0.55:

        return "unknown"

    return detected_intent

# =========================================
# GENERATE RESPONSE
# =========================================

def generate_response(intent):

    if intent in responses:

        return random.choice(
            responses[intent]
        )

    return (
        "Sorry, I could not "
        "understand that."
    )

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )

# =========================================
# CHAT
# =========================================

@app.route("/chat", methods=["POST"])
def chat():

    data = request.json

    user_message = data.get("message")

    print("\nUSER:", user_message)

    intent = detect_intent(
        user_message
    )

    print("INTENT:", intent)

    if intent == "unknown":

        return jsonify({

            "title": "NEXUS AI",

            "message":
            "Sorry, I could not understand that command."
        })

    command = FUNCTIONS[intent]

    result = send_command(command)

    # =====================================
    # SENSOR RESPONSES
    # =====================================

    if intent == "temperature":

        if result is None:

            reply = (
                "ESP32 is not responding."
            )

        elif result == "TEMP_ERROR":

            reply = (
                "Temperature sensor error."
            )

        else:

            reply = (
                f"Current temperature "
                f"is {result}°C 🌡️"
            )

    elif intent == "ldr":

        if result is None:

            reply = (
                "ESP32 is not responding."
            )

        else:

            reply = (
                f"Current LDR value "
                f"is {result} ☀️"
            )

    else:

        reply = generate_response(intent)

    return jsonify({

        "title": "NEXUS AI",

        "message": reply
    })

# =========================================
# RUN APP
# =========================================

if __name__ == "__main__":

    app.run(debug=True)