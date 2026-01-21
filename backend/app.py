from __future__ import annotations

import os
import uuid
from flask import Flask, render_template, request, jsonify
from livekit import api

from backend.config import (
    LIVEKIT_URL, ROOM_PREFIX, IDENTITY_PREFIX,
    LIVEKIT_API_KEY, LIVEKIT_API_SECRET
)
from backend.llm_router import run_agent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    static_url_path="/static",
)

CURRENT = {"room": None, "identity": None}


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/api/start")
def start():
    room = f"{ROOM_PREFIX}-{uuid.uuid4().hex[:8]}"
    identity = f"{IDENTITY_PREFIX}-{uuid.uuid4().hex[:6]}"

    if not (LIVEKIT_API_KEY and LIVEKIT_API_SECRET):
        return jsonify({"error": "LIVEKIT_API_KEY / LIVEKIT_API_SECRET missing in .env"}), 400

    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room,
            can_publish=True,
            can_subscribe=True,
        ))
        .to_jwt()
    )

    CURRENT["room"] = room
    CURRENT["identity"] = identity

    return jsonify({"room": room, "identity": identity, "url": LIVEKIT_URL, "token": token})


@app.post("/api/stop")
def stop():
    CURRENT["room"] = None
    CURRENT["identity"] = None
    return jsonify({"ok": True})


@app.post("/api/ask")
def ask():
    data = request.get_json(silent=True) or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "Empty question"}), 400

    result = run_agent(text)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
