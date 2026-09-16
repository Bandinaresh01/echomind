"""
EchoMind Backend Application.
Flask REST API Server integrating LangGraph, Groq, MCP, and LiveKit,
serving both backend API endpoints and modern production UI.
"""

import os
import logging
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config.settings import settings
from routes.health import health_bp
from routes.chat import chat_bp
from routes.voice import voice_bp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("EchoMind")

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)


def create_app() -> Flask:
    """Application factory for EchoMind Flask API."""
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIST if os.path.exists(FRONTEND_DIST) else None,
        static_url_path=""
    )

    # Enable CORS for frontend clients
    CORS(
        app,
        resources={
            r"/api/*": {"origins": "*"},
            r"/health": {"origins": "*"},
            r"/*": {"origins": "*"}
        },
        supports_credentials=True
    )

    # Register Route Blueprints
    app.register_blueprint(health_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(voice_bp)

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve(path):
        """Serves compiled frontend SPA assets with fallback to API index."""
        if path.startswith("api/") or path.startswith("health"):
            return jsonify({"success": False, "error": f"Endpoint /{path} not found"}), 404

        if path != "" and os.path.exists(os.path.join(FRONTEND_DIST, path)):
            return send_from_directory(FRONTEND_DIST, path)

        if os.path.exists(os.path.join(FRONTEND_DIST, "index.html")):
            return send_from_directory(FRONTEND_DIST, "index.html")

        return jsonify({
            "message": "Welcome to EchoMind Agentic AI Voice + Text Assistant API",
            "version": "3.0.0",
            "endpoints": {
                "health": "GET /health",
                "chat": "POST /api/chat",
                "voice_token": "POST /api/voice/token",
                "voice_status": "GET /api/voice/status"
            },
            "model": settings.GROQ_MODEL
        }), 200

    # Error Handlers returning standardized JSON
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": str(error)}), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}", exc_info=True)
        return jsonify({"success": False, "error": "Internal server error occurred"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    logger.info(f"Starting EchoMind Backend on http://{settings.HOST}:{settings.PORT}")
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG, threaded=True)