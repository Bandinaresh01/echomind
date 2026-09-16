"""
Centralized Configuration Module for EchoMind Backend.
Handles environment variable loading, default values, and validation.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Search for .env file in current directory or parent directory
BASE_DIR = Path(__file__).resolve().parent.parent
PARENT_DIR = BASE_DIR.parent

if (BASE_DIR / ".env").exists():
    load_dotenv(BASE_DIR / ".env")
elif (PARENT_DIR / ".env").exists():
    load_dotenv(PARENT_DIR / ".env")
else:
    load_dotenv()


DEFAULT_SYSTEM_PROMPT = (
    "You are EchoMind, an intelligent AI assistant.\n\n"
    "Rules:\n"
    "1. Understand user question.\n"
    "2. Decide if you need a tool.\n"
    "3. Use search tool for latest information.\n"
    "4. Use weather tool for weather questions.\n"
    "5. Combine tool results with reasoning.\n"
    "6. Give clear answers."
)


class Settings:
    """Application configuration and credentials loader."""

    def __init__(self):
        # Groq Model & Credentials
        self.GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
        self.GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

        # Tool Credentials
        self.WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "").strip()
        self.NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "").strip()

        # LiveKit Credentials
        self.LIVEKIT_URL: str = os.getenv("LIVEKIT_URL", "ws://localhost:7880").strip()
        self.LIVEKIT_API_KEY: str = os.getenv("LIVEKIT_API_KEY", "devkey").strip()
        self.LIVEKIT_API_SECRET: str = os.getenv("LIVEKIT_API_SECRET", "secret").strip()

        # System Prompt
        raw_prompt = os.getenv("SYSTEM_PROMPT", "").strip()
        if raw_prompt:
            # Handle escaped newlines from .env if present
            self.SYSTEM_PROMPT: str = raw_prompt.encode().decode("unicode_escape")
        else:
            self.SYSTEM_PROMPT: str = DEFAULT_SYSTEM_PROMPT

        # Server Settings
        self.PORT: int = int(os.getenv("PORT", "5000"))
        self.HOST: str = os.getenv("HOST", "0.0.0.0")
        self.DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    def has_groq_key(self) -> bool:
        return bool(self.GROQ_API_KEY and self.GROQ_API_KEY != "your_groq_api_key_here")

    def has_weather_key(self) -> bool:
        return bool(self.WEATHER_API_KEY and self.WEATHER_API_KEY != "your_weather_api_key_here")

    def has_news_key(self) -> bool:
        return bool(self.NEWS_API_KEY and self.NEWS_API_KEY != "your_news_api_key_here")

    def has_livekit_credentials(self) -> bool:
        return bool(self.LIVEKIT_API_KEY and self.LIVEKIT_API_SECRET)

    def sanitized_dict(self) -> dict:
        """Returns safe configuration metadata for health checks without exposing secrets."""
        return {
            "groq_model": self.GROQ_MODEL,
            "groq_configured": self.has_groq_key(),
            "weather_configured": self.has_weather_key(),
            "news_configured": self.has_news_key(),
            "livekit_configured": self.has_livekit_credentials(),
            "livekit_url": self.LIVEKIT_URL,
        }


settings = Settings()
