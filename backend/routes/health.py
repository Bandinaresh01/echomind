"""
Health check route.
Provides system diagnostics, Groq model info, and tool statuses.
"""

from flask import Blueprint, jsonify
from config.settings import settings

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
@health_bp.route("/api/health", methods=["GET"])
def health_check():
    """Health probe endpoint returning service status and sanitized configuration."""
    return jsonify({
        "status": "ok",
        "service": "EchoMind Agentic AI Assistant",
        "framework": "Flask + LangGraph + Groq + MCP",
        "groq_model": settings.GROQ_MODEL,
        "tools_available": ["weather_tool", "search_tool", "news_tool", "time_tool"],
        "configuration": settings.sanitized_dict()
    }), 200
