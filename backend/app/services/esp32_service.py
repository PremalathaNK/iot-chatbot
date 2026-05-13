import httpx
from app.utils.config import settings

ESP32_BASE = f"http://{settings.ESP32_IP}"

COMMAND_MAP = {
    "light_on": "/lighton",
    "light_off": "/lightoff",

    "red": "/rgbred",
    "green": "/rgbgreen",
    "blue": "/rgbblue",
    "purple": "/rgbpurple",
    "pink": "/rgbpink",
    "yellow": "/rgbyellow",
    "cyan": "/rgbcyan",
    "white": "/rgbwhite",
    "orange": "/rgborange",

    "dim": "/dim",
    "rgb_off": "/rgboff",

    "relay_on": "/relayon",
    "relay_off": "/relayoff",

    "buzzer_on": "/buzzeron",
    "buzzer_off": "/buzzeroff",

    "melody": "/melody",
    "party": "/disco",

    "temperature": "/temperature",
    "ldr": "/ldr",

    "smart_on": "/smartmode",
    "smart_off": "/smartmodeoff"
}

async def execute_command(command: str):

    if command not in COMMAND_MAP:
        return {
            "success": False,
            "response": "Unknown hardware command"
        }

    url = ESP32_BASE + COMMAND_MAP[command]

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:

            response = await client.get(url)

            if response.status_code == 200:

                return {
                    "success": True,
                    "response": response.text
                }

            return {
                "success": False,
                "response": "ESP32 request failed"
            }

    except Exception as e:

        return {
            "success": False,
            "response": str(e)
        }

async def check_esp32():

    try:
        async with httpx.AsyncClient(timeout=3.0) as client:

            response = await client.get(
                f"{ESP32_BASE}/ping"
            )

            if response.status_code == 200:
                return True

            return False

    except:
        return False