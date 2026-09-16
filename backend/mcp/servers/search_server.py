"""
MCP Search Server.
Provides web search capabilities using DuckDuckGo search engine.
"""

import logging
from typing import Optional
from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun

logger = logging.getLogger("EchoMind.MCP.Search")


class SearchMCPServer:
    """MCP Server providing web search operations."""

    name = "search_mcp_server"
    version = "1.0.0"

    def __init__(self):
        try:
            self.ddg = DuckDuckGoSearchRun()
        except Exception as e:
            logger.error(f"Failed to initialize DuckDuckGoSearchRun: {e}")
            self.ddg = None

    def execute(self, query: str) -> str:
        """Executes a web search for the query and returns formatted text."""
        if not query or not query.strip():
            return "Error: Search query cannot be empty. Please provide a search term."

        q = query.strip()
        logger.info(f"Executing web search for query: {q}")

        if not self.ddg:
            try:
                self.ddg = DuckDuckGoSearchRun()
            except Exception as e:
                return f"Web search engine initialization failed: {str(e)}"

        try:
            results = self.ddg.run(q)
            if not results or not results.strip():
                return f"No search results found for query: '{q}'."
            return results
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            return f"Search operation failed for '{q}': {str(e)}"
