"""
MCP Client Module.
Manages connection and dispatching between EchoMind Agent Tools
and the underlying MCP Tool Servers.
"""

import logging
import time
from typing import Dict, Any, List
from .servers.weather_server import WeatherMCPServer
from .servers.search_server import SearchMCPServer
from .servers.news_server import NewsMCPServer

logger = logging.getLogger("EchoMind.MCP.Client")


class MCPClient:
    """
    Client interface connecting the LangGraph Agent Layer to discrete MCP Servers.
    Maintains server registry, handles unified routing, error isolation, and metrics.
    """

    def __init__(self):
        self.servers: Dict[str, Any] = {
            "weather": WeatherMCPServer(),
            "search": SearchMCPServer(),
            "news": NewsMCPServer(),
        }
        logger.info(f"Initialized MCPClient with servers: {list(self.servers.keys())}")

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns catalog of registered MCP tools and their descriptors."""
        return [
            {
                "name": "weather",
                "description": "Fetch current live weather conditions for any city or location.",
                "server": self.servers["weather"].name,
                "version": self.servers["weather"].version,
                "parameters": {"location": {"type": "string", "description": "City or geographical place name"}},
            },
            {
                "name": "search",
                "description": "Search the live web for facts, documentation, or recent events.",
                "server": self.servers["search"].name,
                "version": self.servers["search"].version,
                "parameters": {"query": {"type": "string", "description": "Search query keywords"}},
            },
            {
                "name": "news",
                "description": "Retrieve the latest news articles and headlines on any topic.",
                "server": self.servers["news"].name,
                "version": self.servers["news"].version,
                "parameters": {"query": {"type": "string", "description": "News topic or keyword"}},
            },
        ]

    def call_tool(self, tool_name: str, **kwargs) -> str:
        """
        Dispatches a tool call to the corresponding MCP server.
        Provides error boundaries and execution timing.
        """
        name = tool_name.lower().replace("_tool", "").strip()
        server = self.servers.get(name)

        if not server:
            err = f"MCP Error: Tool '{tool_name}' is not registered in the MCP Client."
            logger.error(err)
            return err

        start_time = time.time()
        logger.info(f"[MCP Dispatch] Calling server '{server.name}' with args: {kwargs}")

        try:
            if name == "weather":
                location = kwargs.get("location", "")
                result = server.execute(location=location)
            elif name == "search":
                query = kwargs.get("query", "")
                result = server.execute(query=query)
            elif name == "news":
                query = kwargs.get("query", "")
                result = server.execute(query=query)
            else:
                result = f"Unknown tool handler for '{name}'."

            elapsed = round((time.time() - start_time) * 1000, 1)
            logger.info(f"[MCP Success] Server '{server.name}' completed in {elapsed}ms")
            return result

        except Exception as e:
            elapsed = round((time.time() - start_time) * 1000, 1)
            logger.error(f"[MCP Failure] Server '{server.name}' crashed after {elapsed}ms: {e}")
            return f"Error executing tool '{tool_name}' via MCP: {str(e)}"


# Global MCP client singleton
mcp_client = MCPClient()
