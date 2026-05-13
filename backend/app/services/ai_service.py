import json
import httpx

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
# SESSION MEMORY
# =====================================================

SESSION_MEMORY = {

    "last_intent": None,
    "last_rgb": None,

    "rgb_active": False,
    "main_light_active": False,
    "smart_mode": False,
    "buzzer_active": False
}

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
ROLE:
You are NEXUS AI.

You are connected to REAL ESP32 IoT hardware.

You control:
- RGB LEDs
- Main onboard light
- Relay
- Buzzer
- Sensors
- Smart mode

You are intelligent, natural and conversational.

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

ANY COLOR REQUEST means RGB LEDs ONLY.

Examples:

turn on blue light
turn room pink
make room yellow
orange ambience
cyan light
purple glow
red rgb

ALL MUST MAP TO RGB COLORS.

NEVER MAP COLORS TO:
light_on

NEVER TURN ON MAIN LIGHT FOR COLORS.

==================================================

MAIN LIGHT RULES:

ONLY use:
light_on
light_off

IF user CLEARLY says:
- main light
- room light
- onboard light
- normal light
- bulb
- tube light

==================================================

TURN OFF CONTEXT RULES:

After RGB:
turn off
→ rgb_off

After buzzer:
turn off
→ buzzer_off

After smart mode:
turn off
→ smart_off

After main light:
turn off
→ light_off

==================================================

DIM RULES:

Words like:
cozy
dim
sleep
soft
night ambience

→ dim

==================================================

SENSOR RULES:

brightness
light level
ldr
brightness around me
how bright

→ ldr

temperature
how hot
heat

→ temperature

humidity
moisture

→ humidity

==================================================

CHAT RULES:

hello
hi
how are you
good morning
thanks
okay

→ none

==================================================

CRITICAL RULES:

NEVER:
- hallucinate hardware
- change RGB into main light
- randomly change colors
- invent unsupported intents

If uncertain:
intent = none

==================================================

OUTPUT FORMAT:

Return ONLY valid JSON.

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

LAST_INTENT = {SESSION_MEMORY['last_intent']}
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
# NORMALIZE INTENT
# =====================================================

def normalize_intent(intent: str):

    if not intent:
        return "none"

    intent = intent.lower().strip()

    aliases = {

        "lights_on": "light_on",
        "lights_off": "light_off",

        "rgboff": "rgb_off",

        "alarm": "buzzer_on",
        "alarm_off": "buzzer_off",

        "music": "melody",
        "disco": "party"
    }

    if intent in aliases:
        intent = aliases[intent]

    if intent not in VALID_INTENTS:
        return "none"

    return intent

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
# DIRECT RULE ENGINE
# =====================================================

def direct_command(message: str):

    text = message.lower().strip()

    # =================================================
    # TURN OFF
    # =================================================

    if text in [

        "turn off",
        "switch off",
        "off",
        "disable",
        "turn it off"

    ]:

        return smart_turn_off()

    # =================================================
    # RGB OFF
    # =================================================

    if any(x in text for x in [

        "rgb off",
        "turn off rgb",
        "switch off rgb"

    ]):

        return "rgb_off"

    # =================================================
    # MAIN LIGHT
    # =================================================

    if any(x in text for x in [

        "main light",
        "room light",
        "onboard light",
        "normal light",
        "bulb",
        "tube light"

    ]):

        if any(x in text for x in [

            "turn on",
            "switch on",
            "enable"

        ]):

            return "light_on"

        if any(x in text for x in [

            "turn off",
            "switch off",
            "disable"

        ]):

            return "light_off"

    # =================================================
    # RGB COLORS
    # =================================================

    if "red" in text:
        return "red"

    if "green" in text:
        return "green"

    if "blue" in text:
        return "blue"

    if "purple" in text:
        return "purple"

    if "pink" in text:
        return "pink"

    if "yellow" in text:
        return "yellow"

    if "cyan" in text:
        return "cyan"

    if "white" in text and "main" not in text:
        return "white"

    if "orange" in text:
        return "orange"

    # =================================================
    # DIM
    # =================================================

    if any(x in text for x in [

        "dim",
        "cozy",
        "sleep",
        "night",
        "soft light"

    ]):

        return "dim"

    # =================================================
    # PARTY
    # =================================================

    if any(x in text for x in [

        "party",
        "dance",
        "vibe"

    ]):

        return "party"

    # =================================================
    # MELODY
    # =================================================

    if any(x in text for x in [

        "music",
        "song",
        "melody"

    ]):

        return "melody"

    # =================================================
    # BUZZER
    # =================================================

    if any(x in text for x in [

        "buzzer on",
        "alarm",
        "danger",
        "emergency"

    ]):

        return "buzzer_on"

    if any(x in text for x in [

        "buzzer off",
        "stop buzzer"

    ]):

        return "buzzer_off"

    # =================================================
    # RELAY
    # =================================================

    if "relay on" in text:
        return "relay_on"

    if "relay off" in text:
        return "relay_off"

    # =================================================
    # TEMPERATURE
    # =================================================

    if any(x in text for x in [

        "temperature",
        "how hot",
        "heat"

    ]):

        return "temperature"

    # =================================================
    # HUMIDITY
    # =================================================

    if "humidity" in text:
        return "humidity"

    # =================================================
    # LDR
    # =================================================

    if any(x in text for x in [

        "brightness",
        "ldr",
        "light level",
        "how bright"

    ]):

        return "ldr"

    # =================================================
    # SMART MODE
    # =================================================

    if any(x in text for x in [

        "smart mode on",
        "enable smart mode"

    ]):

        return "smart_on"

    if any(x in text for x in [

        "smart mode off",
        "disable smart mode"

    ]):

        return "smart_off"

    return None

# =====================================================
# MAIN PROCESSOR
# =====================================================

async def process_message(message: str):

    try:

        # =================================================
        # DIRECT RULE ENGINE FIRST
        # =================================================

        direct = direct_command(message)

        if direct:

            intent = direct
            ai_reply = None

        else:

            raw = await ask_model(message)

            parsed = extract_json(raw)

            if not parsed:

                return {
                    "reply":
                    "I couldn't understand that properly."
                }

            intent = normalize_intent(
                parsed.get("intent")
            )

            ai_reply = parsed.get(
                "response",
                "Done"
            )

        # =================================================
        # CHAT ONLY
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

        print(f"\nINTENT: {intent}")
        print(f"RESULT: {result}")

        if not result["success"]:

            return {
                "reply":
                f"ESP32 ERROR: {result['response']}"
            }

        # =================================================
        # UPDATE MEMORY
        # =================================================

        SESSION_MEMORY["last_intent"] = intent

        if intent in RGB_COLORS:

            SESSION_MEMORY["rgb_active"] = True
            SESSION_MEMORY["last_rgb"] = intent

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
        # HARDWARE RESPONSES
        # =================================================

        responses = {

            "light_on":
            "Main light turned on 💡",

            "light_off":
            "Main light turned off 🌑",

            "red":
            "Red RGB light turned on 🔴",

            "green":
            "Green RGB light turned on 🟢",

            "blue":
            "Blue RGB light turned on 🔵",

            "purple":
            "Purple RGB light turned on 🟣",

            "pink":
            "Pink RGB light turned on 🌸",

            "yellow":
            "Yellow RGB light turned on 💛",

            "cyan":
            "Cyan RGB light turned on 💠",

            "orange":
            "Orange RGB light turned on 🟠",

            "white":
            "White RGB light turned on ⚪",

            "rgb_off":
            "RGB lighting turned off ⚫",

            "dim":
            "Dim ambience activated 🌙",

            "party":
            "Party mode activated 🕺🎉",

            "melody":
            "Playing melody 🎵",

            "relay_on":
            "Relay switched ON ⚡",

            "relay_off":
            "Relay switched OFF ⭕",

            "buzzer_on":
            "Buzzer activated 🚨",

            "buzzer_off":
            "Buzzer turned off 🔕",

            "smart_on":
            "Smart mode enabled 🤖",

            "smart_off":
            "Smart mode disabled 🛑"
        }

        return {
            "reply":
            responses.get(
                intent,
                ai_reply or "Done"
            )
        }

    except Exception as e:

        return {
            "reply":
            f"AI processing error: {str(e)}"
        }