"""
News tool for LangGraph Agent.
Invokes the News MCP Server via the unified MCP Client.
"""

from langchain_core.tools import tool
from mcp.client import mcp_client


@tool
def news_tool(query: str = "") -> str:
    """
    Fetch the latest news headlines and articles regarding a specific topic.
    Use this tool whenever the user asks for current news, today's headlines,
    recent events, or updates on politics, technology, AI, sports, etc.
    Input should be a search query summarizing the news topic.
    """
    return mcp_client.call_tool("news", query=query)
