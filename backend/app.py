
from flask import Flask, render_template, request, jsonify
import requests
import random

app = Flask(__name__)

ESP32_IP = "http://10.61.103.174"   # CHANGE TO YOUR ESP32 IP

# ----------------------------
# SEND COMMAND TO ESP32
# ----------------------------
def send_command(cmd):
    try:
        r = requests.get(f"{ESP32_IP}/{cmd}", timeout=3)
        return r.text
    except:
        return None
# ----------------------------
# CHAT RESPONSES
# ----------------------------
def ai_reply(command):
    cmd = command.lower()

    # LIGHT ON
    if any(x in cmd for x in ["light on", "turn on light", "turn on the light"]):
        send_command("lighton")
        return {
            "title": "💡 LIGHT ON",
            "message": "The room is glowing now ✨"
        }

    # LIGHT OFF
    elif any(x in cmd for x in ["light off", "turn off light", "turn off the light"]):
        send_command("lightoff")
        return {
            "title": "🌑 LIGHT OFF",
            "message": "Lights turned off successfully 🌙"
        }

    # RGB RED
    elif any(x in cmd for x in ["rgb red", "set rgb red", "red light"]):
        send_command("rgbred")
        return {
            "title": "🔴 RGB RED",
            "message": "RGB changed to RED ❤️"
        }

    # RGB BLUE
    elif any(x in cmd for x in ["rgb blue", "set rgb blue", "blue light"]):
        send_command("rgbblue")
        return {
            "title": "🔵 RGB BLUE",
            "message": "RGB changed to BLUE 💙"
        }
        # RGB OFF
    elif any(x in cmd for x in ["rgb off", "turn off rgb", "switch off rgb"]):
        send_command("rgboff")
        return {
            "title": "⚫ RGB OFF",
            "message": "RGB LEDs are now OFF 🌑"
        }

    # TEMPERATURE
    elif any(x in cmd for x in ["temperature", "temp", "show temperature"]):
        data = send_command("temp")

        if data:
            return {
                "title": "🌡️ TEMPERATURE",
                "message": f"Current temperature is {data}°C"
            }

        return {
            "title": "⚠️ ERROR",
            "message": "Could not read temperature sensor"
        }

    # LDR
    elif any(x in cmd for x in ["ldr", "light level", "check ldr"]):
        data = send_command("ldr")

        if data:
            return {
                "title": "☀️ LDR SENSOR",
                "message": f"Current LDR value: {data}"
            }

        return {
            "title": "⚠️ ERROR",
            "message": "Could not read LDR sensor"
        }
    # MELODY
    elif any(x in cmd for x in ["music", "melody", "play melody", "play music"]):
        send_command("melody")
        return {
            "title": "🎵 MELODY",
            "message": "Playing a relaxing melody for you 🎶"
        }

    # RELAY ON
    elif any(x in cmd for x in ["relay on", "turn on relay"]):
        send_command("relayon")
        return {
            "title": "⚡ RELAY ON",
            "message": "Relay switched ON successfully ⚡"
        }

    # RELAY OFF
    elif any(x in cmd for x in ["relay off", "turn off relay"]):
        send_command("relayoff")
        return {
            "title": "⭕ RELAY OFF",
            "message": "Relay switched OFF successfully"
        }

    # BUZZER ON
    elif any(x in cmd for x in ["buzzer on", "alarm on"]):
        send_command("buzzeron")
        return {
            "title": "🚨 BUZZER ON",
            "message": "Alarm buzzer activated 🚨"
        }

    # BUZZER OFF
    elif any(x in cmd for x in ["buzzer off", "alarm off"]):
        send_command("buzzeroff")
        return {
            "title": "🔕 BUZZER OFF",
            "message": "Alarm buzzer turned OFF"
        }
    # SMART MODE
    elif any(x in cmd for x in ["smart mode", "auto mode"]):
        send_command("smartmode")
        return {
            "title": "🤖 SMART MODE",
            "message": "Smart street light mode activated 🌃"
        }

    return {
        "title": "🤔 UNKNOWN COMMAND",
        "message": "Try commands like light on, rgb red, melody, buzzer on"
    }


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    command = data.get("message")

    response = ai_reply(command)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)