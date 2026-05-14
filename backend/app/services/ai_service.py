import json
import httpx
import difflib

from app.utils.config import settings
from app.services.esp32_service import execute_command

# =====================================================
# VALID INTENTS
# =====================================================

VALID_INTENTS = {

    "light_on",
    "light_off",

    "red",
    "green",
    "blue",
    "purple",
    "pink",
    "yellow",
    "cyan",
    "white",
    "orange",

    "dim",
    "rgb_off",

    "relay_on",
    "relay_off",

    "buzzer_on",
    "buzzer_off",

    "party",
    "melody",

    "temperature",
    "humidity",
    "ldr",

    "smart_on",
    "smart_off",

    "none"
}

# =====================================================
# RGB COLORS
# =====================================================

RGB_COLORS = {

    "red",
    "green",
    "blue",
    "purple",
    "pink",
    "yellow",
    "cyan",
    "white",
    "orange"
}

# =====================================================
# MEMORY
# =====================================================

SESSION_MEMORY = {

    "last_intent": None,
    "last_rgb": None,

    "rgb_active": False,
    "main_light_active": False,
    "buzzer_active": False,
    "smart_mode": False
}

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are SST AIoT Chatbot.

You are connected to REAL ESP32 hardware.

You are conversational and intelligent.
greet properly with hi hello how are you and such kind of greeting texts

BUT:
You MUST NEVER trigger wrong hardware.

==================================================

AVAILABLE INTENTS:

light_on
light_off

red
green
blue
purple
pink
yellow
cyan
white
orange

dim
rgb_off

relay_on
relay_off

buzzer_on
buzzer_off

party
melody

temperature
humidity
ldr

smart_on
smart_off

none

==================================================

VERY IMPORTANT RGB RULES:

ANY COLOR REQUEST ALWAYS MEANS RGB LED.

Examples:

green light
yellow ambience
make room blue
cyan glow
pink rgb
orange color

ALL MUST MAP TO RGB COLORS.

NEVER convert color requests into:
light_on

==================================================

MAIN LIGHT RULES:
If only asked turn on lights 
room is dark
room is too bright
ONLY use:
light_on
light_off

if user EXPLICITLY says:

main light
bulb
normal light
tube light
onboard light

==================================================

TURN OFF RULES:

After RGB:
turn off → rgb_off

After buzzer:
turn off → buzzer_off

After smart mode:
turn off → smart_off

After main light:
turn off → light_off

==================================================

If uncertain:
intent = none

==================================================

Return ONLY JSON.

{
  "intent": "valid_intent",
  "response": "natural conversational response"
}
"""

# =====================================================
# ASK MODEL
# =====================================================

async def ask_model(message: str):

    memory = f"""

LAST_RGB = {SESSION_MEMORY['last_rgb']}
RGB_ACTIVE = {SESSION_MEMORY['rgb_active']}
MAIN_LIGHT_ACTIVE = {SESSION_MEMORY['main_light_active']}
BUZZER_ACTIVE = {SESSION_MEMORY['buzzer_active']}
SMART_MODE = {SESSION_MEMORY['smart_mode']}

"""

    payload = {

        "model": settings.MODEL_NAME,

        "prompt":
        f"{SYSTEM_PROMPT}\n{memory}\nUser: {message}",

        "stream": False
    }

    async with httpx.AsyncClient(timeout=60.0) as client:

        response = await client.post(
            settings.OLLAMA_URL,
            json=payload
        )

        data = response.json()

        return data.get("response", "")

# =====================================================
# EXTRACT JSON
# =====================================================

def extract_json(text: str):

    try:

        start = text.find("{")
        end = text.rfind("}")

        if start == -1 or end == -1:
            return None

        return json.loads(text[start:end+1])

    except:
        return None

# =====================================================
# TYPO COLOR DETECTION
# =====================================================

def detect_color_typo(text):

    words = text.lower().split()

    for word in words:

        # ignore very small words
        if len(word) < 4:
            continue

        match = difflib.get_close_matches(
            word,
            list(RGB_COLORS),
            n=1,
            cutoff=0.82
        )

        if match:
            return match[0]

    return None
# =====================================================
# SMART TURN OFF
# =====================================================

def smart_turn_off():

    if SESSION_MEMORY["buzzer_active"]:
        return "buzzer_off"

    if SESSION_MEMORY["smart_mode"]:
        return "smart_off"

    if SESSION_MEMORY["rgb_active"]:
        return "rgb_off"

    if SESSION_MEMORY["main_light_active"]:
        return "light_off"

    return "rgb_off"

# =====================================================
# RULE ENGINE
# =====================================================

def rule_engine(message: str):

    text = message.lower().strip()

    # =================================================
    # TURN OFF
    # =================================================

    if text in [

        "turn off",
        "switch off",
        "off",
        "turn it off"

    ]:

        return smart_turn_off()

    # =================================================
    # COLOR TYPO FIX
    # =================================================

    typo_color = detect_color_typo(text)

    if typo_color:
        return typo_color

    # =================================================
    # RGB COLORS
    # =================================================

    for color in RGB_COLORS:

        if color in text:
            return color

    # =================================================
    # RGB OFF
    # =================================================

    if "rgb off" in text:
        return "rgb_off"

    # =================================================
    # MAIN LIGHT
    # =================================================

    if any(x in text for x in [

        "main light",
        "normal light",
        "bulb",
        "tube light"

    ]):

        if any(x in text for x in [

            "on",
            "enable"

        ]):

            return "light_on"

        if any(x in text for x in [

            "off",
            "disable"

        ]):

            return "light_off"

    # =================================================
    # BUZZER
    # =================================================

    if any(x in text for x in [

        "alarm",
        "buzzer",
        "emergency"

    ]):

        if "off" in text:
            return "buzzer_off"

        return "buzzer_on"

    # =================================================
    # PARTY
    # =================================================

    if any(x in text for x in [

        "party",
        "dance",
        "club",
        "vibe"

    ]):

        return "party"

    # =================================================
    # MUSIC
    # =================================================

    if any(x in text for x in [

        "music",
        "song",
        "melody"

    ]):

        return "melody"

    # =================================================
    # DIM
    # =================================================

    if any(x in text for x in [

        "cozy",
        "sleep",
        "dim",
        "soft light"

    ]):

        return "dim"

    # =================================================
    # SENSOR
    # =================================================

    if any(x in text for x in [

        "temperature",
        "weather",
        "hot"

    ]):

        return "temperature"

    if "humidity" in text:
        return "humidity"

    if any(x in text for x in [

        "brightness",
        "light level",
        "bright"

    ]):

        return "ldr"

    return None

# =====================================================
# MAIN PROCESSOR
# =====================================================

async def process_message(message: str):

    try:

        # =================================================
        # RULE ENGINE FIRST
        # =================================================

        intent = rule_engine(message)

        ai_reply = None

        # =================================================
        # AI IF RULE ENGINE FAILS
        # =================================================

        if not intent:

            raw = await ask_model(message)

            print(raw)

            parsed = extract_json(raw)

            if not parsed:

                return {
                    "reply":
                    "I couldn't understand that properly."
                }

            intent = parsed.get(
                "intent",
                "none"
            )

            ai_reply = parsed.get(
                "response",
                "Done"
            )

        # =================================================
        # VALIDATE INTENT
        # =================================================

        if intent not in VALID_INTENTS:
            intent = "none"

        # =================================================
        # CHAT
        # =================================================

        if intent == "none":

            return {
                "reply":
                ai_reply or "Hello 👋"
            }

        # =================================================
        # EXECUTE HARDWARE
        # =================================================

        result = await execute_command(intent)

        print(intent)
        print(result)

        if not result["success"]:

            return {
                "reply":
                "ESP32 communication failed."
            }

        # =================================================
        # UPDATE MEMORY
        # =================================================

        SESSION_MEMORY["last_intent"] = intent

        if intent in RGB_COLORS:

            SESSION_MEMORY["rgb_active"] = True
            SESSION_MEMORY["last_rgb"] = intent
            SESSION_MEMORY["main_light_active"] = False

        if intent == "rgb_off":
            SESSION_MEMORY["rgb_active"] = False

        if intent == "light_on":
            SESSION_MEMORY["main_light_active"] = True

        if intent == "light_off":
            SESSION_MEMORY["main_light_active"] = False

        if intent == "buzzer_on":
            SESSION_MEMORY["buzzer_active"] = True

        if intent == "buzzer_off":
            SESSION_MEMORY["buzzer_active"] = False

        if intent == "smart_on":
            SESSION_MEMORY["smart_mode"] = True

        if intent == "smart_off":
            SESSION_MEMORY["smart_mode"] = False

        # =================================================
        # SENSOR RESPONSES
        # =================================================

        if intent == "temperature":

            return {
                "reply":
                f"Current temperature is {result['response']} °C 🌡️"
            }

        if intent == "humidity":

            return {
                "reply":
                f"Current humidity is {result['response']} % 💧"
            }

        if intent == "ldr":

            return {
                "reply":
                f"Current brightness level is {result['response']} ☀️"
            }

        # =================================================
        # AI RESPONSE
        # =================================================

        if ai_reply:

            return {
                "reply":
                ai_reply
            }

        # =================================================
        # DEFAULT RESPONSES
        # =================================================

        responses = {

            "light_on":
            "Main light turned on 💡",

            "light_off":
            "Main light turned off 🌑",

            "rgb_off":
            "RGB lighting turned off ⚫",

            "red":
            "Red RGB light activated 🔴",

            "green":
            "Green RGB light activated 🟢",

            "blue":
            "Blue RGB light activated 🔵",

            "yellow":
            "Yellow RGB light activated 💛",

            "pink":
            "Pink RGB light activated 🌸",

            "purple":
            "Purple RGB light activated 🟣",

            "cyan":
            "Cyan RGB light activated 💠",

            "orange":
            "Orange RGB light activated 🟠",

            "white":
            "White RGB light activated ⚪",

            "party":
            "Party mode activated 🕺🎉",

            "melody":
            "Playing melody 🎵",

            "buzzer_on":
            "Buzzer activated 🚨",

            "buzzer_off":
            "Alarm silenced 🔕",

            "smart_on":
            "Smart mode enabled 🤖",

            "smart_off":
            "Smart mode disabled 🛑",

            "dim":
            "Dim ambience activated 🌙"
        }

        return {
            "reply":
            responses.get(intent, "Done")
        }

    except Exception as e:

        return {
            "reply":
            f"AI processing error: {str(e)}"
        }