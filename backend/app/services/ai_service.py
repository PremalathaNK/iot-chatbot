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
    "ldr",

    "smart_on",
    "smart_off",

    "none"
}

# =====================================================
# SESSION MEMORY
# =====================================================

SESSION_MEMORY = {
    "last_intent": None,
    "smart_mode": False,
    "last_light_mode": None
}

# =====================================================
# SYSTEM PROMPT
# =====================================================

SYSTEM_PROMPT = """
You are NEXUS AI Smart IoT Assistant.

You control REAL IoT hardware connected to an ESP32.

Your job:
- Understand natural human language
- Detect user intention
- Control hardware correctly
- Be conversational and friendly
- Never invent fake sensor values
- Never pretend hardware executed if it failed

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
ldr
smart_on
smart_off
none

VERY IMPORTANT RULES:

- Return ONLY valid JSON
- Never return markdown
- Never explain JSON
- Never create new intent names
- Use ONLY the exact intents listed above

Examples:

User: make room pink
{
  "intent": "pink",
  "response": "Sure 🌸 Changing the room lights to pink."
}

User: turn off smart mode
{
  "intent": "smart_off",
  "response": "Okay 🛑 Disabling smart mode now."
}

User: play music
{
  "intent": "melody",
  "response": "Alright 🎵 Playing a melody for you."
}

User: i am bored
{
  "intent": "party",
  "response": "Let's make the room more fun 🕺"
}

User: what is the temperature
{
  "intent": "temperature",
  "response": "Checking the current temperature 🌡️"
}

User: hello
{
  "intent": "none",
  "response": "Hello 👋 How can I help you today?"
}

FINAL OUTPUT FORMAT:

{
  "intent": "exact_intent_name",
  "response": "natural conversational response"
}
"""

# =====================================================
# CONTEXT OVERRIDE
# =====================================================

def contextual_intent(message: str):

    text = message.lower()

    # =================================================
    # DIM LIGHTING
    # =================================================

    if any(x in text for x in [

        "dim light",
        "dim lights",
        "dimmer",
        "sleep light",
        "night lamp",
        "soft light",
        "low light",
        "i am sleeping",
        "going to sleep",
        "sleep now"

    ]):
        return "dim"

    # =================================================
    # TOO BRIGHT
    # =================================================

    if any(x in text for x in [

        "too bright",
        "very bright",
        "make it dark",
        "hurting my eyes"

    ]):
        return "light_off"

    # =================================================
    # TOO DARK
    # =================================================

    if any(x in text for x in [

        "too dark",
        "cannot see",
        "not able to see",
        "need light",
        "it is dark"

    ]):
        return "light_on"

    # =================================================
    # MUSIC
    # =================================================

    if any(x in text for x in [

        "play music",
        "music",
        "song"

    ]):
        return "melody"

    # =================================================
    # PANIC / EMERGENCY
    # =================================================

    if any(x in text for x in [

        "panic",
        "emergency",
        "danger",
        "alarm",
        "siren"

    ]):
        return "buzzer_on"

    return None

# =====================================================
# ASK MODEL
# =====================================================

async def ask_model(message: str):

    payload = {
        "model": settings.MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\nUser: {message}",
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

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        return None

    try:

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

        "turn_on_light": "light_on",
        "lights_on": "light_on",

        "turn_off_light": "light_off",
        "lights_off": "light_off",

        "panic_mode": "buzzer_on",
        "alarm": "buzzer_on",

        "mute_alarm": "buzzer_off",

        "sleep_mode": "dim",

        "music": "melody",

        "disco": "party"
    }

    if intent in aliases:
        intent = aliases[intent]

    if intent not in VALID_INTENTS:
        return "none"

    return intent

# =====================================================
# MAIN PROCESSOR
# =====================================================

async def process_message(message: str):

    try:

        lower = message.lower()

        # =================================================
        # CONTEXTUAL OVERRIDE FIRST
        # =================================================

        forced_intent = contextual_intent(message)

        if forced_intent:

            result = await execute_command(forced_intent)

            if result["success"]:

                responses = {

                    "dim":
                    "Alright 🌙 Setting the room to a soft dim light for comfort.",

                    "light_on":
                    "It's pretty dark around you — turning the lights on now 💡",

                    "light_off":
                    "Got it 🌑 Reducing the brightness by turning the lights off.",

                    "melody":
                    "Alright 🎵 Playing a melody for you.",

                    "buzzer_on":
                    "Emergency alarm activated 🚨"
                }

                return {
                    "reply":
                    responses.get(
                        forced_intent,
                        "Done"
                    )
                }

            return {
                "reply":
                "ESP32 communication failed"
            }

        # =================================================
        # GENERIC TURN OFF HANDLING
        # =================================================

        if lower in [
            "turn off",
            "switch off",
            "disable it"
        ]:

            if SESSION_MEMORY["smart_mode"]:

                intent = "smart_off"

            else:

                intent = "rgb_off"

            result = await execute_command(intent)

            if result["success"]:

                if intent == "smart_off":

                    SESSION_MEMORY["smart_mode"] = False

                    return {
                        "reply":
                        "Okay 🛑 Smart mode has been disabled."
                    }

                return {
                    "reply":
                    "Alright ⚫ Turning off the lights."
                }

            return {
                "reply":
                "ESP32 communication failed"
            }

        # =================================================
        # ASK AI MODEL
        # =================================================

        raw = await ask_model(message)

        parsed = extract_json(raw)

        if not parsed:

            return {
                "reply":
                "AI response parsing failed"
            }

        intent = normalize_intent(
            parsed.get("intent", "none")
        )

        ai_reply = parsed.get(
            "response",
            "Done"
        )

        # =================================================
        # NO HARDWARE ACTION
        # =================================================

        if intent == "none":

            return {
                "reply": ai_reply
            }

        # =================================================
        # EXECUTE HARDWARE
        # =================================================

        result = await execute_command(intent)

        if not result["success"]:

            return {
                "reply":
                "ESP32 communication failed"
            }

        # =================================================
        # UPDATE MEMORY
        # =================================================

        SESSION_MEMORY["last_intent"] = intent

        if intent == "smart_on":
            SESSION_MEMORY["smart_mode"] = True

        if intent == "smart_off":
            SESSION_MEMORY["smart_mode"] = False

        if intent in [

            "red",
            "green",
            "blue",
            "purple",
            "pink",
            "yellow",
            "cyan",
            "white",
            "orange",
            "dim"

        ]:

            SESSION_MEMORY["last_light_mode"] = intent

        # =================================================
        # REAL SENSOR VALUES
        # =================================================

        if intent == "temperature":

            return {
                "reply":
                f"Current temperature is {result['response']} °C 🌡️"
            }

        if intent == "ldr":

            return {
                "reply":
                f"Current brightness sensor value is {result['response']} ☀️"
            }

        # =================================================
        # FRIENDLY RESPONSES
        # =================================================

        responses = {

            "light_on":
            "Sure 💡 Turning the lights on.",

            "light_off":
            "Okay 🌑 Turning the lights off.",

            "dim":
            "Alright 🌙 Dimming the lights for a softer atmosphere.",

            "party":
            "Party mode activated 🕺🎉 Enjoy the vibe!",

            "melody":
            "Playing a melody for you 🎵",

            "buzzer_on":
            "Emergency buzzer activated 🚨",

            "buzzer_off":
            "Alarm silenced 🔕",

            "smart_on":
            "Smart mode enabled 🤖",

            "smart_off":
            "Smart mode disabled 🛑",

            "rgb_off":
            "RGB lighting turned off ⚫",

            "red":
            "The room is glowing red 🔴",

            "blue":
            "Switching the room to blue 🔵",

            "green":
            "Setting the room lights to green 🟢",

            "pink":
            "The room now has a beautiful pink glow 🌸",

            "white":
            "Changing the room lighting to white ⚪",

            "purple":
            "Purple lighting enabled 🟣",

            "yellow":
            "Yellow ambient lighting enabled 🟡",

            "cyan":
            "Cyan lighting activated 💠",

            "orange":
            "Orange mood lighting enabled 🟠",

            "relay_on":
            "Relay switched ON ⚡",

            "relay_off":
            "Relay switched OFF ⭕"
        }

        return {
            "reply":
            responses.get(intent, ai_reply)
        }

    except Exception as e:

        return {
            "reply":
            f"AI processing error: {str(e)}"
        }