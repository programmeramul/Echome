"""
ECHOME Configuration Settings

Local-first personal AI clone configuration.
All values are overridable via environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# === Ollama Settings ===
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3.2:3b")
MODEL_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"

# === Server Settings ===
HOST = os.getenv("ECHOME_HOST", "127.0.0.1")
PORT = int(os.getenv("ECHOME_PORT", "7860"))
DEBUG = os.getenv("ECHOME_DEBUG", "false").lower() == "true"

# === Memory Settings ===
DB_PATH = Path(os.getenv("ECHOME_DB_PATH", str(Path.home() / ".echome" / "memory.db")))
MEMORY_ENABLED = os.getenv("ECHOME_MEMORY", "true").lower() == "true"

# === Speech Settings ===
ASR_MODEL = os.getenv("ASR_MODEL", "whisper-small")  # AI4Bharat IndicConformer or Whisper
TTS_ENGINE = os.getenv("TTS_ENGINE", "pyttsx3")  # Lightweight local TTS
SUPPORTED_LANGUAGES = ["en", "hi", "kn"]

# === Voice Cloning Settings ===
VOICE_CLONING_ENABLED = os.getenv("ECHOME_VOICE_CLONING", "false").lower() == "true"
VOICE_CLONING_MODEL = os.getenv("VOICE_CLONING_MODEL", "")

# === Privacy Settings ===
PRIVATE_MODE = os.getenv("ECHOME_PRIVATE", "true").lower() == "true"
BIND_ADDRESS = os.getenv("ECHOME_BIND", "127.0.0.1")


class Settings:
    """Runtime configuration container."""

    def __init__(self):
        self.ollama_base_url = OLLAMA_BASE_URL
        self.default_model = DEFAULT_MODEL
        self.model_endpoint = MODEL_ENDPOINT
        self.host = HOST
        self.port = PORT
        self.debug = DEBUG
        self.db_path = DB_PATH
        self.memory_enabled = MEMORY_ENABLED
        self.asr_model = ASR_MODEL
        self.tts_engine = TTS_ENGINE
        self.supported_languages = SUPPORTED_LANGUAGES
        self.voice_cloning_enabled = VOICE_CLONING_ENABLED
        self.voice_cloning_model = VOICE_CLONING_MODEL
        self.private_mode = PRIVATE_MODE
        self.bind_address = BIND_ADDRESS


# Singleton instance
settings = Settings()

# Validate directories
DB_PATH.parent.mkdir(parents=True, exist_ok=True)