#tools/weather_tool.py
import requests
def get_weather_raw(location: str) -> str:
    """
    Uses wttr.in public endpoint (no API key).
    Returns raw text for Gemini to refine.
    """
    location = (location or "").strip()
    if not location:
        location = "Hyderabad"

    url = f"https://wttr.in/{location}?format=3"  # short one-line summary
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "EchoMind/1.0"})
        r.raise_for_status()
        return r.text.strip()
    except Exception as e:
        return f"Weather tool error: {type(e).__name__}: {e}"
