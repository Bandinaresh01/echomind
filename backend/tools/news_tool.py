
#tools/news_tool.py
import requests
from backend.config import NEWS_API_KEY, NEWS_COUNTRY


def get_news_raw(topic: str | None = None, *, limit: int = 7) -> str:
    """
    Uses NewsAPI.org. Needs NEWS_API_KEY in .env.
    Returns raw headlines for Gemini to summarize.
    """
    if not NEWS_API_KEY:
        return "NEWS_API_KEY is missing in .env. Add it to enable News tool."

    base = "https://newsapi.org/v2/top-headlines"
    params = {"apiKey": NEWS_API_KEY, "pageSize": limit, "country": NEWS_COUNTRY}

    if topic and topic.strip():
        # using 'q' keeps it simple
        params["q"] = topic.strip()

    try:
        r = requests.get(base, params=params, timeout=12)
        r.raise_for_status()
        data = r.json()
        articles = data.get("articles", []) or []

        if not articles:
            return "No news results found."

        lines = []
        for i, a in enumerate(articles, start=1):
            title = a.get("title") or "Untitled"
            source = (a.get("source") or {}).get("name") or "Unknown"
            url = a.get("url") or ""
            lines.append(f"{i}. {title} — {source}\n   {url}")

        return "\n".join(lines)
    except Exception as e:
        return f"News tool error: {type(e).__name__}: {e}"
