"""
Model Context Protocol (MCP) Layer for EchoMind.
Provides standardized MCP Server & Client architecture for tools.
"""

from .client import mcp_client

__all__ = ["mcp_client"]
