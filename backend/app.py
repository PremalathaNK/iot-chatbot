
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import requests
import torch
import re

# =========================================================
# FLASK SETUP
# =========================================================

app = Flask(__name__)
CORS(app)

# =========================================================
# ESP32 CONFIG
# =========================================================

ESP32_IP = "http://10.61.103.174"

# =========================================================
# LOAD AI MODEL
# =========================================================

print("Loading AI Model...")

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("AI Model Loaded Successfully")

# =========================================================
# COMMAND DATABASE
# =========================================================

COMMANDS = {

    # LIGHTS
    "/lighton": [
        "light on",
        "turn on light",
        "switch on light",
        "lights on",
        "enable lights",
        "room light on",
        "illuminate room"
    ],

    "/lightoff": [
        "light off",
        "turn off light",
        "switch off lights",
        "lights off",
        "disable lights",
        "dark room"
    ],

    # RGB COLORS
    "/rgbred": [
        "red light",
        "make room red",
        "turn light red",
        "red color"
    ],

    "/rgbgreen": [
        "green light",
        "make room green",
        "green color"
    ],

    "/rgbblue": [
        "blue light",
        "make room blue",
        "blue color"
    ],

    "/rgbpurple": [
        "purple light",
        "violet light",
        "purple color"
    ],

    "/rgbpink": [
        "pink light",
        "pink color",
        "rose color"
    ],

    "/rgbyellow": [
        "yellow light",
        "warm yellow",
        "yellow color"
    ],

    "/rgbcyan": [
        "cyan light",
        "sky blue",
        "cyan color"
    ],

    "/rgbwhite": [
        "white light",
        "normal white",
        "bright white"
    ],

    "/rgborange": [
        "orange light",
        "sunset orange",
        "orange color"
    ],

    "/rgboff": [
        "rgb off",
        "turn rgb off",
        "disable rgb",
        "stop rgb"
    ],

    # MODES
    "/dim": [
        "dim light",
        "night mode",
        "low brightness",
        "ambient light",
        "sleep light"
    ],

    "/disco": [
        "party mode",
        "dance mode",
        "disco mode",
        "celebration lights"
    ],

    "/smartmode": [
        "smart mode",
        "automatic mode",
        "ai lighting",
        "enable smart mode"
    ],

    "/smartmodeoff": [
        "disable smart mode",
        "smart mode off",
        "stop smart mode"
    ],

    # RELAY
    "/relayon": [
        "relay on",
        "power on",
        "switch relay on"
    ],

    "/relayoff": [
        "relay off",
        "power off",
        "switch relay off"
    ],

    # BUZZER
    "/buzzeron": [
        "buzzer on",
        "alarm on",
        "enable buzzer"
    ],

    "/buzzeroff": [
        "buzzer off",
        "alarm off",
        "disable buzzer",
        "silent mode"
    ],

    # MELODY
    "/melody": [
        "play melody",
        "play music",
        "music",
        "melody"
    ],

    # TEMPERATURE
    "/temperature": [
        "temperature",
        "room temperature",
        
        "how hot is room",
        "current temperature"
    ],

    # HUMIDITY
    "/humidity": [
        "humidity",
        "room humidity",
        "moisture level",
        "air humidity"
    ],

    # LDR
    "/ldr": [
        "ldr value",
        "light intensity",
        "brightness",
        "ambient light",
        "light sensor value"
    ]
}

# =========================================================
# RESPONSE DATABASE
# =========================================================

RESPONSES = {

    "/lighton":
    "💡 Lights turned ON",

    "/lightoff":
    "🌑 Lights turned OFF",

    "/rgbred":
    "🔴 Red lighting activated",

    "/rgbgreen":
    "🟢 Green lighting activated",

    "/rgbblue":
    "🔵 Blue lighting activated",

    "/rgbpurple":
    "🟣 Purple lighting activated",

    "/rgbpink":
    "🌸 Pink lighting activated",

    "/rgbyellow":
    "🟡 Yellow lighting activated",

    "/rgbcyan":
    "💠 Cyan lighting activated",

    "/rgbwhite":
    "⚪ White lighting activated",

    "/rgborange":
    "🟠 Orange lighting activated",

    "/rgboff":
    "⚫ RGB lighting disabled",

    "/dim":
    "🌙 Dim ambient lighting enabled",

    "/disco":
    "🎉 Party mode activated",

    "/smartmode":
    "🤖 Smart AI lighting enabled",

    "/smartmodeoff":
    "🛑 Smart mode disabled",

    "/relayon":
    "⚡ Relay switched ON",

    "/relayoff":
    "⭕ Relay switched OFF",

    "/buzzeron":
    "🚨 Buzzer enabled",

    "/buzzeroff":
    "🔕 Buzzer disabled",

    "/melody":
    "🎵 Melody started"
}

# =========================================================
# PREPARE AI EMBEDDINGS
# =========================================================

all_sentences = []
sentence_to_endpoint = {}

for endpoint, phrases in COMMANDS.items():

    for phrase in phrases:

        all_sentences.append(phrase)

        sentence_to_endpoint[phrase] = endpoint

print("Creating embeddings...")

embeddings = model.encode(
    all_sentences,
    convert_to_tensor=True
)

print("Embeddings Ready")

# =========================================================
# TEXT CLEANER
# =========================================================

def clean_text(text):

    text = text.lower()

    text = re.sub(
        r'[^a-zA-Z0-9\s]',
        '',
        text
    )

    return text.strip()

# =========================================================
# AI UNDERSTANDING
# =========================================================

def find_best_command(user_input):

    user_input = clean_text(user_input)

    user_embedding = model.encode(
        user_input,
        convert_to_tensor=True
    )

    scores = util.cos_sim(
        user_embedding,
        embeddings
    )[0]

    best_index = torch.argmax(scores).item()

    best_score = scores[
        best_index
    ].item()

    matched_sentence = all_sentences[
        best_index
    ]

    endpoint = sentence_to_endpoint[
        matched_sentence
    ]

    print("\n====================")
    print("USER:", user_input)
    print("MATCH:", matched_sentence)
    print("ENDPOINT:", endpoint)
    print("SCORE:", best_score)
    print("====================\n")

    # threshold
    if best_score < 0.45:

        return None

    return endpoint

# =========================================================
# SEND COMMAND TO ESP32
# =========================================================

def send_command(endpoint):

    try:

        url = ESP32_IP + endpoint

        print("Sending:", url)

        response = requests.get(
            url,
            timeout=5
        )

        print("ESP32 Response:", response.text)

        if response.status_code == 200:

            return response.text.strip()

        return None

    except Exception as e:

        print("ESP ERROR:", e)

        return None

# =========================================================
# ROOT
# =========================================================

@app.route("/")

def home():

    return render_template("index.html")

# =========================================================
# STATUS
# =========================================================

@app.route("/status")


@app.route("/status")
def status():

    try:

        response = requests.get(
            ESP32_IP + "/ping",
            timeout=3
        )

        if response.status_code == 200:

            return jsonify({
                "status": "online"
            })

    except Exception as e:

        print("STATUS ERROR:", e)

    return jsonify({
        "status": "offline"
    })
# =========================================================
# CHAT API
# =========================================================

@app.route("/chat", methods=["POST"])

def chat():

    try:

        data = request.get_json()

        user_message = data.get(
            "message",
            ""
        )

        if user_message.strip() == "":

            return jsonify({
                "reply":
                "Please enter a command"
            })

        # =========================================
        # AI UNDERSTANDING
        # =========================================

        endpoint = find_best_command(
            user_message
        )

        if endpoint is None:

            return jsonify({
                "reply":
                "I couldn't understand that command."
            })

        # =========================================
        # SEND TO ESP32
        # =========================================

        esp_response = send_command(
            endpoint
        )

        if esp_response is None:

            return jsonify({
                "reply":
                "ESP32 not responding ❌"
            })

        # =========================================
        # TEMPERATURE
        # =========================================

        if endpoint == "/temperature":

            return jsonify({
                "reply":
                f"🌡 Temperature: {esp_response} °C"
            })

        # =========================================
        # HUMIDITY
        # =========================================

        if endpoint == "/humidity":

            return jsonify({
                "reply":
                f"💧 Humidity: {esp_response} %"
            })

        # =========================================
        # LDR
        # =========================================

        if endpoint == "/ldr":

            return jsonify({
                "reply":
                f"☀ Ambient Light Value: {esp_response}"
            })

        # =========================================
        # NORMAL RESPONSE
        # =========================================

        return jsonify({
            "reply":
            RESPONSES.get(
                endpoint,
                "Command executed successfully ✅"
            )
        })

    except Exception as e:

        print("SERVER ERROR:", e)

        return jsonify({
            "reply":
            "Internal server error ❌"
        })

# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )