"""
Unit tests for EchoMind MCP Tools.
Tests weather, search, news, and time tools for valid output and graceful error handling.
"""

import pytest
from tools.time_tool import time_tool
from tools.weather import weather_tool
from tools.news import news_tool
from tools.search import search_tool
from mcp.client import mcp_client


def test_mcp_client_catalog():
    """Verify MCP client discovers all registered tools."""
    tools = mcp_client.list_tools()
    tool_names = [t["name"] for t in tools]
    assert "weather" in tool_names
    assert "search" in tool_names
    assert "news" in tool_names


def test_time_tool():
    """Verify time tool requires no arguments and returns a valid formatted string."""
    result = time_tool.invoke({})
    assert "The current date and time is" in result
    assert len(result) > 20


def test_weather_tool_valid_city():
    """Verify weather tool retrieves live weather for a known city."""
    result = weather_tool.invoke({"location": "Hyderabad"})
    assert isinstance(result, str)
    assert len(result) > 10
    # Should mention temperature or weather
    assert "°C" in result or "weather" in result.lower() or "hyderabad" in result.lower()


def test_weather_tool_invalid_location():
    """Verify weather tool handles invalid or nonexistent city gracefully."""
    result = weather_tool.invoke({"location": "FakeCityXYZ_NotReal_99999"})
    assert isinstance(result, str)
    assert "not found" in result.lower() or "could not" in result.lower() or "error" in result.lower()


def test_weather_tool_empty_input():
    """Verify weather tool handles empty string gracefully."""
    result = weather_tool.invoke({"location": ""})
    assert isinstance(result, str)
    assert "cannot be empty" in result.lower() or "error" in result.lower()


def test_search_tool_valid_query():
    """Verify search tool queries DuckDuckGo successfully."""
    result = search_tool.invoke({"query": "Python programming language"})
    assert isinstance(result, str)
    assert len(result) > 20


def test_search_tool_empty_query():
    """Verify search tool handles empty query."""
    result = search_tool.invoke({"query": ""})
    assert isinstance(result, str)
    assert "cannot be empty" in result.lower() or "error" in result.lower()


def test_news_tool_valid_topic():
    """Verify news tool fetches recent articles."""
    result = news_tool.invoke({"query": "artificial intelligence"})
    assert isinstance(result, str)
    assert len(result) > 20


def test_news_tool_default_topic():
    """Verify news tool handles blank query by searching general technology news."""
    result = news_tool.invoke({"query": ""})
    assert isinstance(result, str)
    assert len(result) > 20
