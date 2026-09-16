"""
Voice routes for LiveKit WebRTC token generation and voice state management.
"""

import logging
import uuid
from datetime import timedelta
from flask import Blueprint, request, jsonify
from livekit import api
from config.settings import settings

logger = logging.getLogger("EchoMind.Routes.Voice")

voice_bp = Blueprint("voice", __name__)


@voice_bp.route("/api/voice/token", methods=["POST"])
def get_voice_token():
    """
    Generates a cryptographically signed LiveKit AccessToken for real-time audio rooms.
    Accepts JSON:
      {
        "room_name": "string (optional)",
        "participant_name": "string (optional)"
      }
    Returns:
      {
        "success": true,
        "token": "JWT...",
        "url": "ws://localhost:7880",
        "room": "echomind-room",
        "participant": "user-xyz"
      }
    """
    data = request.get_json(silent=True) or {}
    room_name = data.get("room_name", "").strip() or f"echomind-room"
    participant_name = data.get("participant_name", "").strip() or f"user-{uuid.uuid4().hex[:6]}"

    if not settings.has_livekit_credentials():
        logger.warning("LiveKit API credentials missing. Returning warning.")
        return jsonify({
            "success": False,
            "error": "LiveKit credentials (LIVEKIT_API_KEY, LIVEKIT_API_SECRET) not configured."
        }), 500

    try:
        token = (
            api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET)
            .with_identity(participant_name)
            .with_name(participant_name)
            .with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,
                    can_subscribe=True,
                )
            )
            .with_ttl(timedelta(hours=2))
            .to_jwt()
        )

        logger.info(f"Generated LiveKit token for participant '{participant_name}' in room '{room_name}'")

        return jsonify({
            "success": True,
            "token": token,
            "url": settings.LIVEKIT_URL,
            "room": room_name,
            "participant": participant_name
        }), 200

    except Exception as e:
        logger.error(f"Failed to generate LiveKit token: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error": f"Failed to generate voice token: {str(e)}"
        }), 500


@voice_bp.route("/api/voice/status", methods=["GET"])
def voice_status():
    """Checks Voice service and LiveKit configuration readiness."""
    configured = settings.has_livekit_credentials()
    return jsonify({
        "success": True,
        "livekit_configured": configured,
        "livekit_url": settings.LIVEKIT_URL,
        "supported_states": ["IDLE", "CONNECTING", "LISTENING", "PROCESSING", "SPEAKING"],
        "speech_fallback_supported": True
    }), 200
