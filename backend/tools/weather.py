"""
Weather tool for LangGraph Agent.
Invokes the Weather MCP Server via the unified MCP Client.
"""

from langchain_core.tools import tool
from mcp.client import mcp_client


@tool
def weather_tool(location: str) -> str:
    """
    Fetch the current live weather and temperature for a given location or city.
    Use this tool whenever the user asks about the weather, temperature, humidity,
    or atmospheric conditions in a specific city or region.
    Input should be a city name (e.g., 'Hyderabad', 'Tokyo', 'New York').
    """
    return mcp_client.call_tool("weather", location=location)
