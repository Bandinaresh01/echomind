"""
Integration tests for EchoMind Flask REST API endpoints.
"""

import json
import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_root_endpoint(client):
    """Verify root API returns service info and routes."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert "EchoMind" in data["message"]


def test_health_endpoint(client):
    """Verify health check returns ok status and tool catalog."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert "weather_tool" in data["tools_available"]


def test_chat_missing_body(client):
    """Verify chat endpoint rejects empty payload."""
    res = client.post("/api/chat", json={})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False
    assert "invalid" in data["error"].lower() or "empty" in data["error"].lower()


def test_chat_empty_query(client):
    """Verify chat endpoint rejects whitespace query."""
    res = client.post("/api/chat", json={"query": "   "})
    assert res.status_code == 400
    data = res.get_json()
    assert data["success"] is False


def test_voice_status(client):
    """Verify voice status endpoint returns configuration flags."""
    res = client.get("/api/voice/status")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "livekit_configured" in data


def test_voice_token_generation(client):
    """Verify LiveKit access token generation."""
    res = client.post("/api/voice/token", json={
        "room_name": "test-room",
        "participant_name": "test-user"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["token"]) > 50
    assert data["room"] == "test-room"
    assert data["participant"] == "test-user"
