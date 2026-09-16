"""
MCP News Server.
Provides recent news headlines and articles using NewsAPI.org
with fallback to DuckDuckGo News Search.
"""

import logging
import requests
from config.settings import settings
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun

logger = logging.getLogger("EchoMind.MCP.News")


class NewsMCPServer:
    """MCP Server providing live news retrieval."""

    name = "news_mcp_server"
    version = "1.0.0"

    def __init__(self):
        self.timeout = 8

    def execute(self, query: str = "") -> str:
        """
        Fetches latest news matching the query.
        Uses NewsAPI if configured, falling back to DuckDuckGo news search.
        """
        search_query = query.strip() if query and query.strip() else "latest artificial intelligence technology"
        logger.info(f"Fetching news for topic: {search_query}")

        # Strategy 1: NewsAPI with NEWS_API_KEY
        if settings.has_news_key():
            try:
                newsapi_result = self._fetch_newsapi(search_query)
                if newsapi_result:
                    return newsapi_result
            except Exception as e:
                logger.warning(f"NewsAPI query failed ({e}), falling back to search...")

        # Strategy 2: DuckDuckGo news search fallback
        try:
            return self._fetch_ddg_news(search_query)
        except Exception as e:
            logger.error(f"News fallback search failed: {e}")
            return f"Unable to retrieve news for '{search_query}': {str(e)}"

    def _fetch_newsapi(self, query: str) -> str:
        """Queries NewsAPI.org v2/everything endpoint."""
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": settings.NEWS_API_KEY,
            "pageSize": 5,
            "sortBy": "publishedAt",
            "language": "en"
        }

        resp = requests.get(url, params=params, timeout=self.timeout)

        if resp.status_code == 200:
            data = resp.json()
            articles = data.get("articles", [])
            if not articles:
                logger.info(f"NewsAPI returned 0 articles for query '{query}', trying fallback.")
                return ""

            lines = [f"### Latest News on '{query}':"]
            for i, art in enumerate(articles[:5], 1):
                title = art.get("title", "Untitled")
                source = art.get("source", {}).get("name", "Unknown Source")
                desc = art.get("description", "No description available.")
                url_link = art.get("url", "")
                pub_date = art.get("publishedAt", "")[:10]

                lines.append(f"{i}. **{title}** ({source}, {pub_date})")
                if desc:
                    lines.append(f"   {desc}")
                if url_link:
                    lines.append(f"   Source: {url_link}")

            return "\n".join(lines)
        else:
            logger.warning(f"NewsAPI returned status {resp.status_code}: {resp.text}")
            return ""

    def _fetch_ddg_news(self, query: str) -> str:
        """Queries DuckDuckGo specifically for news topics."""
        ddg = DuckDuckGoSearchRun()
        news_query = f"{query} news headlines"
        result = ddg.run(news_query)
        if result and result.strip():
            return f"### Recent News Updates for '{query}':\n{result}"
        return f"No recent news articles found for '{query}'."
