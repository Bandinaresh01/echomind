
import os
import uuid
from flask import Flask, jsonify, send_from_directory, request
from dotenv import load_dotenv

from livekit.api.access_token import AccessToken, VideoGrants

from stt import WhisperRoomSTT
from llm import ask_gemini

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "ws://localhost:7880")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# --- STT worker (joins room as "stt-agent" + transcribes) ---
stt_worker = WhisperRoomSTT(
    livekit_url=LIVEKIT_URL,
    api_key=LIVEKIT_API_KEY,
    api_secret=LIVEKIT_API_SECRET,
    whisper_model=WHISPER_MODEL,
)
stt_worker.start_background()

# --- store last Q/A ---
last_answer = ""
last_question = ""


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/style.css")
def serve_css():
    return send_from_directory(app.static_folder, "style.css")


@app.route("/api/start", methods=["POST"])
def api_start():
    """
    Starts a new LiveKit room session:
    - Creates a new room name
    - Returns {url, room, identity, token}
    - Tells STT worker to join the same room and listen
    """
    global last_answer, last_question
    last_answer = ""
    last_question = ""

    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return jsonify({"error": "LIVEKIT_API_KEY / LIVEKIT_API_SECRET missing in .env"}), 500

    room = f"echomind-{uuid.uuid4().hex[:8]}"
    identity = f"user-{uuid.uuid4().hex[:6]}"

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_grants(
            VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
        .to_jwt()
    )

    stt_worker.connect(room_name=room)

    return jsonify({
        "url": LIVEKIT_URL,
        "room": room,
        "identity": identity,
        "token": token
    })


@app.route("/api/stop", methods=["POST"])
def api_stop():
    stt_worker.disconnect()
    return jsonify({"ok": True})


@app.route("/api/speech", methods=["GET"])
def api_speech():
    """Latest transcript produced by local whisper."""
    return jsonify({"text": stt_worker.last_text})


@app.route("/api/ask", methods=["POST"])
def api_ask():
    """Send the user question to Gemini and return answer."""
    global last_answer, last_question

    data = request.get_json(silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "question is required"}), 400

    last_question = question
    answer = ask_gemini(question)
    last_answer = answer

    return jsonify({"answer": answer})


@app.route("/api/answer", methods=["GET"])
def api_answer():
    return jsonify({"question": last_question, "answer": last_answer})


@app.route("/api/debug", methods=["GET"])
def api_debug():
    return jsonify({
        "livekit_url": LIVEKIT_URL,
        "whisper_model": WHISPER_MODEL,
        "stt": stt_worker.debug_state(),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        "has_google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
