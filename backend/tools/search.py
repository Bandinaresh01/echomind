"""
Web search tool for LangGraph Agent.
Invokes the Search MCP Server via the unified MCP Client.
"""

from langchain_core.tools import tool
from mcp.client import mcp_client


@tool
def search_tool(query: str) -> str:
    """
    Search the live web using DuckDuckGo.
    Use this tool when the user asks questions that require current knowledge,
    recent facts, online information, technical lookups, or documentation
    that may not be part of the training data.
    Input should be a clear, concise search query.
    """
    return mcp_client.call_tool("search", query=query)
