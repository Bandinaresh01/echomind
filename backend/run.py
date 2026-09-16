"""
Startup runner for EchoMind Backend.
Usage: python run.py
"""

from app import app
from config.settings import settings

if __name__ == "__main__":
    print(f"==================================================")
    print(f" EchoMind Backend Running on http://{settings.HOST}:{settings.PORT}")
    print(f" Groq Model: {settings.GROQ_MODEL}")
    print(f" LiveKit URL: {settings.LIVEKIT_URL}")
    print(f"==================================================")
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG, threaded=True)
