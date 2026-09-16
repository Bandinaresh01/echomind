"""
Chat endpoints for EchoMind.
Handles conversation requests, LangGraph invocation, and SSE streaming.
"""

import asyncio
import logging
from flask import Blueprint, request, Response, jsonify, stream_with_context
from agents.graph import stream_agent_events, run_agent

logger = logging.getLogger("EchoMind.Routes.Chat")

chat_bp = Blueprint("chat", __name__)


def generate_sse(query: str, history: list):
    """
    Synchronous generator wrapping the async LangGraph event stream
    for Flask WSGI compliance.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        async_gen = stream_agent_events(query, history)
        while True:
            try:
                chunk = loop.run_until_complete(async_gen.__anext__())
                yield chunk
            except StopAsyncIteration:
                break
            except Exception as e:
                logger.error(f"Error in SSE generator: {e}")
                yield f"data: {{\"type\": \"error\", \"content\": \"Stream error: {str(e)}\"}}\n\n"
                break
    finally:
        loop.close()


@chat_bp.route("/api/chat", methods=["POST"])
def chat_endpoint():
    """
    Primary chat endpoint.
    Accepts JSON:
      {
        "query": "string (required)",
        "history": [{"role": "user"|"assistant", "content": "string"}] (optional),
        "stream": true|false (optional, default: true)
      }
    Returns:
      - text/event-stream (SSE) when stream=True
      - application/json when stream=False
    """
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid request body. Expected JSON object."}), 400

    query = data.get("query", "").strip()
    if not query:
        return jsonify({"success": False, "error": "Query cannot be empty."}), 400

    history = data.get("history", [])
    if not isinstance(history, list):
        history = []

    is_stream = data.get("stream", True)
    if request.args.get("stream", "").lower() == "false":
        is_stream = False

    logger.info(f"Received chat request: '{query[:60]}...' (stream={is_stream})")

    # Non-streaming JSON mode (useful for testing and API clients)
    if not is_stream:
        try:
            result = run_agent(query, history)
            return jsonify({
                "success": True,
                "response": result["response"],
                "tools_used": result["tools_used"]
            }), 200
        except Exception as e:
            logger.error(f"Error executing agent: {e}", exc_info=True)
            return jsonify({"success": False, "error": str(e)}), 500

    # Streaming mode (SSE)
    response = Response(
        stream_with_context(generate_sse(query, history)),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Content-Type": "text/event-stream",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
    return response
