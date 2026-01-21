#tools/web_search.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


def duckduckgo_search_raw(query: str, *, limit: int = 5) -> str:
    """
    Scrapes DuckDuckGo HTML results (no API key).
    Returns titles + snippets + links.
    """
    query = (query or "").strip()
    if not query:
        return "Search query is empty."

    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        r = requests.get(url, timeout=12, headers={"User-Agent": "EchoMind/1.0"})
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.select(".result")[:limit]

        if not results:
            return "No web results found."

        out = []
        for i, item in enumerate(results, start=1):
            a = item.select_one(".result__a")
            snippet = item.select_one(".result__snippet")
            title = a.get_text(" ", strip=True) if a else "Untitled"
            link = a["href"] if a and a.has_attr("href") else ""
            snip = snippet.get_text(" ", strip=True) if snippet else ""
            out.append(f"{i}. {title}\n   {snip}\n   {link}")

        return "\n".join(out)
    except Exception as e:
        return f"Search tool error: {type(e).__name__}: {e}"
