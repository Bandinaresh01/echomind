import os
import sys
import uuid
import subprocess
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv
from livekit.api.access_token import AccessToken, VideoGrants

load_dotenv()

app = Flask(__name__, static_folder="../frontend", static_url_path="")

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/token")
def token():
    if not LIVEKIT_URL or not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        return jsonify({"error": "Missing LIVEKIT_URL / LIVEKIT_API_KEY / LIVEKIT_API_SECRET in .env"}), 500

    room_name = f"echomind-{uuid.uuid4().hex[:8]}"

    at = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity("user1")
        .with_grants(VideoGrants(room_join=True, room=room_name, can_publish=True, can_subscribe=True))
    )
    return jsonify({"token": at.to_jwt(), "url": LIVEKIT_URL, "room": room_name})

def start_agent_worker():
    worker_path = os.path.join(os.path.dirname(__file__), "agent_worker.py")
    cmd = [sys.executable, worker_path, "dev"]
    print("✅ Starting agent worker subprocess:", " ".join(cmd))
    return subprocess.Popen(cmd)

if __name__ == "__main__":
    start_agent_worker()
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
