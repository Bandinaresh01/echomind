
#llm_router.py
from __future__ import annotations
import json
import re

from backend.config import ENABLE_LLM_TOOL_SELECTION
from backend.llm import ask_gemini
from backend.tools.weather_tool import get_weather_raw
from backend.tools.news_tool import get_news_raw
from backend.tools.web_search import duckduckgo_search_raw

TOOLS = ["weather", "news", "web_search", "llm_only"]


def _heuristic_route(user_text: str) -> dict:
    t = (user_text or "").lower()

    if any(k in t for k in ["weather", "temperature", "rain", "forecast", "climate"]):
        return {"tool": "weather", "args": {"location": _extract_location(user_text)}}

    if any(k in t for k in ["news", "headlines", "breaking", "latest news", "today news", "technology news", "sports news"]):
        return {"tool": "news", "args": {"topic": _extract_topic(user_text)}}

    if any(k in t for k in ["search", "google", "duckduckgo", "find", "look up"]) or len(user_text.split()) >= 6:
        return {"tool": "web_search", "args": {"query": user_text}}

    return {"tool": "llm_only", "args": {}}


def _extract_location(text: str) -> str:
    m = re.search(r"weather in ([a-zA-Z\s]+)", text, re.I)
    return (m.group(1).strip() if m else "").strip() or "Hyderabad"


def _extract_topic(text: str) -> str:
    cleaned = re.sub(r"\b(news|headlines|today|latest|breaking)\b", "", text, flags=re.I).strip()
    return cleaned or "technology"


def _llm_route(user_text: str) -> dict:
    selector_prompt = f"""
You are a tool-router. Choose the best tool for the user question.
Prefer llm_only for general knowledge questions that can be answered with known information.

Tools:
- weather: for weather/temperature/forecast questions
- news: for headlines/latest news questions
- web_search: for questions needing fresh web info, references, or explanations
- llm_only: for general knowledge or reasoning that does not need tools

Return ONLY valid JSON in this schema:
{{
  "tool": "weather|news|web_search|llm_only",
  "args": {{ ... }}
}}

User question:
{user_text}
""".strip()

    res = ask_gemini(selector_prompt).text

    try:
        data = json.loads(_extract_json(res))
        tool = data.get("tool")
        if tool not in TOOLS:
            raise ValueError("invalid tool")
        args = data.get("args", {}) or {}
        return {"tool": tool, "args": args}
    except Exception:
        return _heuristic_route(user_text)


def _extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end + 1]
    return "{}"


def run_agent(user_text: str) -> dict:
    route = _llm_route(user_text) if ENABLE_LLM_TOOL_SELECTION else _heuristic_route(user_text)
    tool = route["tool"]
    args = route.get("args", {}) or {}

    if tool == "weather":
        raw = get_weather_raw(args.get("location", "Hyderabad"))
        prompt = f"Raw weather info:\n{raw}\n\nUser asked: {user_text}\nExplain clearly."
        answer = ask_gemini(prompt).text
        return {"tool_used": tool, "raw_data": raw, "answer": answer}

    if tool == "news":
        raw = get_news_raw(args.get("topic"))
        prompt = f"Raw news headlines:\n{raw}\n\nUser asked: {user_text}\nSummarize in bullet points, mention sources briefly."
        answer = ask_gemini(prompt).text
        return {"tool_used": tool, "raw_data": raw, "answer": answer}

    if tool == "web_search":
        raw = duckduckgo_search_raw(args.get("query", user_text))
        prompt = f"Web search results:\n{raw}\n\nUser asked: {user_text}\nAnswer using these results. If unsure, say so."
        answer = ask_gemini(prompt).text
        return {"tool_used": tool, "raw_data": raw, "answer": answer}

    answer = ask_gemini(user_text).text
    return {"tool_used": "llm_only", "raw_data": "", "answer": answer}
