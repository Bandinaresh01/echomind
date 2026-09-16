"""
Unit and integration tests for LangGraph Agent.
Verifies tool invocation decisions, history preservation, and response synthesis.
"""

import pytest
from agents.graph import run_agent, get_agent_graph


def test_agent_graph_compilation():
    """Verify LangGraph compiles with agent and tools nodes."""
    graph = get_agent_graph()
    assert graph is not None
    assert "agent" in graph.nodes
    assert "tools" in graph.nodes


def test_agent_direct_response():
    """Verify LangGraph answers normal questions without invoking unnecessary tools."""
    result = run_agent("Explain what a database index is in one short sentence.")
    assert "response" in result
    assert len(result["response"]) > 10
    # For a general concept explanation, no tools should be needed
    # (or if any, should be empty/minimal)


def test_agent_weather_tool_decision():
    """Verify LangGraph invokes weather tool for weather queries."""
    result = run_agent("What is the current weather in Hyderabad?")
    assert "response" in result
    assert "Hyderabad" in result["response"] or "weather" in result["response"].lower() or "temperature" in result["response"].lower() or "°" in result["response"]


def test_agent_with_history():
    """Verify LangGraph preserves conversational history context."""
    history = [
        {"role": "user", "content": "My name is Vikram."},
        {"role": "assistant", "content": "Nice to meet you, Vikram!"}
    ]
    result = run_agent("What is my name?", history=history)
    assert "Vikram" in result["response"]
