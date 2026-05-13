def detect_intent(message: str):

    text = message.lower()

    # =========================================
    # LIGHT ON
    # =========================================

    if any(word in text for word in [
        "light on",
        "turn on light",
        "switch on light",
        "illuminate",
        "brighten room"
    ]):
        return "light_on"

    # =========================================
    # LIGHT OFF
    # =========================================

    if any(word in text for word in [
        "light off",
        "turn off light",
        "switch off light",
        "dark room"
    ]):
        return "light_off"

    # =========================================
    # DIM
    # =========================================

    if any(word in text for word in [
        "dim",
        "dimmer",
        "low light",
        "night mode",
        "sleep",
        "sleeping",
        "dark",
        "darker"
    ]):
        return "dim"

    # =========================================
    # PARTY MODE
    # =========================================

    if any(word in text for word in [
        "party",
        "dance",
        "music lights",
        "disco",
        "bored",
        "fun mode"
    ]):
        return "party"

    # =========================================
    # BUZZER / ALARM
    # =========================================

    if any(word in text for word in [
        "alarm",
        "emergency",
        "siren",
        "panic",
        "danger",
        "alert",
        "buzzer on"
    ]):
        return "buzzer_on"

    if any(word in text for word in [
        "stop alarm",
        "disable alarm",
        "silent",
        "mute",
        "buzzer off",
        "turn off buzzer"
    ]):
        return "buzzer_off"

    # =========================================
    # RELAY
    # =========================================

    if any(word in text for word in [
        "relay on",
        "start relay"
    ]):
        return "relay_on"

    if any(word in text for word in [
        "relay off",
        "stop relay"
    ]):
        return "relay_off"

    # =========================================
    # SMART MODE
    # =========================================

    if any(word in text for word in [
        "smart mode",
        "enable smart",
        "automatic mode",
        "ai mode"
    ]):
        return "smart_on"

    if any(word in text for word in [
        "disable smart",
        "turn off smart",
        "smart off"
    ]):
        return "smart_off"

    # =========================================
    # TEMPERATURE
    # =========================================

    if any(word in text for word in [
        "temperature",
        "how hot",
        "how cold",
        "air temperature",
        "climate"
    ]):
        return "temperature"

    # =========================================
    # LDR
    # =========================================

    if any(word in text for word in [
        "brightness",
        "ldr",
        "light level"
    ]):
        return "ldr"

    # =========================================
    # COLORS
    # =========================================

    colors = {
        "red": "red",
        "blue": "blue",
        "green": "green",
        "purple": "purple",
        "pink": "pink",
        "yellow": "yellow",
        "cyan": "cyan",
        "white": "white",
        "orange": "orange"
    }

    for key, value in colors.items():

        if key in text:
            return value

    # =========================================
    # OFF
    # =========================================

    if any(word in text for word in [
        "turn off",
        "switch off",
        "shutdown",
        "power off"
    ]):
        return "rgb_off"

    return None