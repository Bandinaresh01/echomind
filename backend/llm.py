#llm.py
from __future__ import annotations
from dataclasses import dataclass

from backend.config import GOOGLE_API_KEY, GEMINI_MODEL, GEMINI_SYSTEM_PROMPT


@dataclass
class LLMResult:
    text: str


def ask_gemini(user_prompt: str, *, system_prompt: str | None = None, model_name: str | None = None) -> LLMResult:
    if not GOOGLE_API_KEY:
        return LLMResult("GOOGLE_API_KEY is missing in .env. Add it to enable Gemini answers.")

    try:
        import google.generativeai as genai
    except Exception:
        return LLMResult("Gemini SDK not installed. Run: pip install google-generativeai")

    genai.configure(api_key=GOOGLE_API_KEY)

    model = genai.GenerativeModel(model_name or GEMINI_MODEL)
    system = system_prompt or GEMINI_SYSTEM_PROMPT

    full_prompt = f"{system}\n\nUser: {user_prompt}\nAssistant:"

    try:
        resp = model.generate_content(full_prompt)
        text = getattr(resp, "text", "") or ""
        text = text.strip()
        return LLMResult(text if text else "I couldn't generate a response.")
    except Exception as e:
        return LLMResult(f"Gemini error: {type(e).__name__}: {e}")
