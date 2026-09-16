"""
LangGraph Tools Registry for EchoMind.
Exports tools ready to bind to Groq LLM in LangGraph.
"""

from .weather import weather_tool
from .search import search_tool
from .news import news_tool
from .time_tool import time_tool

ALL_TOOLS = [weather_tool, search_tool, news_tool, time_tool]

__all__ = [
    "weather_tool",
    "search_tool",
    "news_tool",
    "time_tool",
    "ALL_TOOLS",
]
