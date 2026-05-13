from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", 8000))

    ESP32_IP = os.getenv("ESP32_IP")

    OLLAMA_URL = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434/api/generate"
    )

    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "llama3.2:3b"
    )

settings = Settings()