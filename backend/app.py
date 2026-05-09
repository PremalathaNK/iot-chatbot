from flask import Flask, render_template
from flask import request, jsonify

import requests
import random

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
        "rgb red",
        "turn on red"
    ],

    "rgb_blue": [

        "blue light",
        "make room blue",
        "blue ambience",
        "rgb blue"
    ],

    "rgb_green": [

        "green light",
        "make room green",
        "rgb green"
    ],

    "rgb_off": [

        "turn off rgb",
        "disable rgb",
        "rgb off",
        "remove ambient lights",
        "turn off red",
        "turn off blue",
        "turn off green"
    ],

    "buzzer_on": [

        "turn on alarm",
        "alert me",
        "activate buzzer",
        "danger alert",
        "wake me up",
        "start alarm",
        "buzzer on"
    ],

    "buzzer_off": [

        "turn off alarm",
        "disable buzzer",
        "stop alert",
        "alarm off",
        "buzzer off"
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
        "smart mode off",
        "stop smart lighting"
    ],

    "temperature": [

        "temperature",
        "how hot is it",
        "current temperature",
        "room temperature"
    ],

    "humidity": [

        "humidity",
        "room humidity",
        "air humidity"
    ],

    "ldr": [

        "ldr value",
        "light level",
        "brightness level",
        "ldr"
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
    "humidity": "humidity",

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
# CLEAN TEXT
# =========================================

def clean_text(text):

    text = text.lower()

    fixes = {

        "turn of": "turn off",
        "trun": "turn",
        "ligth": "light",
        "alaram": "alarm",
        "musci": "music",
        "part mode": "party mode"
    }

    for wrong, correct in fixes.items():

        text = text.replace(
            wrong,
            correct
        )

    return text

# =========================================
# SEND COMMAND TO ESP32
# =========================================

def send_command(command):

    try:

        url = f"{ESP32_IP}/{command}"

        print("REQUEST:", url)

        response = requests.get(
            url,
            timeout=8
        )

        print("ESP32 RESPONSE:", response.text)

        return response.text.strip()

    except Exception as e:

        print("ESP32 ERROR:", e)

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

    # RGB OFF

    if any(x in msg for x in [

        "rgb off",
        "turn off rgb",
        "disable rgb",
        "turn off red",
        "turn off blue",
        "turn off green"
    ]):

        return "rgb_off"

    # RGB RED

    if "red" in msg:

        return "rgb_red"

    # RGB BLUE

    if "blue" in msg:

        return "rgb_blue"

    # RGB GREEN

    if "green" in msg:

        return "rgb_green"

    # SMART MODE

    if "smart mode" in msg:

        if "off" in msg:

            return "smart_mode_off"

        return "smart_mode_on"

    # BUZZER

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
            "dim"
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

    # HUMIDITY

    if "humidity" in msg:

        return "humidity"

    # LDR

    if "ldr" in msg:

        return "ldr"

    # =====================================
    # AI SEMANTIC SEARCH
    # =====================================

    user_embedding = model.encode([msg])

    similarities = cosine_similarity(

        user_embedding,
        sentence_embeddings
    )

    best_index = similarities.argmax()

    confidence = similarities[0][best_index]

    detected_intent = all_intents[best_index]

    print("CONFIDENCE:", confidence)
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

    return "Sorry, I could not understand that."

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

    print("FINAL INTENT:", intent)

    if intent == "unknown":

        return jsonify({

            "title": "NEXUS AI",

            "message":
            "Sorry, I could not understand that command."
        })

    command = FUNCTIONS[intent]

    result = send_command(command)

    # =====================================
    # DEVICE OFFLINE
    # =====================================

    if result is None:

        return jsonify({

            "title": "NEXUS AI",

            "message":
            "ESP32 is not responding."
        })

    # =====================================
    # TEMPERATURE
    # =====================================

    if intent == "temperature":

        try:

            temp = float(result)

            reply = (
                f"Current temperature is "
                f"{temp:.1f}°C 🌡️"
            )

        except:

            reply = (
                "Temperature sensor error."
            )

    # =====================================
    # HUMIDITY
    # =====================================

    elif intent == "humidity":

        try:

            humidity = float(result)

            reply = (
                f"Current humidity is "
                f"{humidity:.1f}% 💧"
            )

        except:

            reply = (
                "Humidity sensor error."
            )

    # =====================================
    # LDR
    # =====================================

    elif intent == "ldr":

        reply = (
            f"Current LDR value "
            f"is {result} ☀️"
        )

    # =====================================
    # NORMAL RESPONSES
    # =====================================

    else:

        reply = generate_response(intent)

    return jsonify({

        "title": "NEXUS AI",

        "message": reply
    })

# =========================================
# MAIN
# =========================================

if __name__ == "__main__":

    print("\nNEXUS AI")
    print("System initialized successfully 🚀")

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )