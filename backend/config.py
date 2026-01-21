#config.py
import os
from dotenv import load_dotenv

load_dotenv()


def env(key: str, default: str | None = None) -> str | None:
    v = os.getenv(key)
    return v if v not in (None, "") else default


# LiveKit (self-hosted docker)
LIVEKIT_URL = env("LIVEKIT_URL", "ws://localhost:7880")  # ws:// for local
LIVEKIT_API_KEY = env("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = env("LIVEKIT_API_SECRET")

ROOM_PREFIX = env("LIVEKIT_ROOM_PREFIX", "echomind")
IDENTITY_PREFIX = env("LIVEKIT_IDENTITY_PREFIX", "user")

# Gemini
GOOGLE_API_KEY = env("GOOGLE_API_KEY")
GEMINI_MODEL = env("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_SYSTEM_PROMPT = env(
    "GEMINI_SYSTEM_PROMPT",
    "You are EchoMind, a helpful assistant. Answer clearly, step-by-step when needed, and be concise."
)

# News
NEWS_API_KEY = env("NEWS_API_KEY")  # optional
NEWS_COUNTRY = env("NEWS_COUNTRY", "in")  # default India

# Router behavior
ENABLE_LLM_TOOL_SELECTION = (env("ENABLE_LLM_TOOL_SELECTION", "true") or "true").lower() == "true"
