"""
Groq LLM Client Module.
Manages ChatGroq model instance creation, parameters, and key validation.
"""

import logging
from typing import Optional
from langchain_groq import ChatGroq
from config.settings import settings

logger = logging.getLogger("EchoMind.LLM.Groq")


def get_groq_llm(
    streaming: bool = True,
    temperature: float = 0.7,
    max_retries: int = 2
) -> ChatGroq:
    """
    Instantiates and returns a configured ChatGroq LLM.
    Uses centralized GROQ_MODEL and GROQ_API_KEY from settings.
    """
    if not settings.has_groq_key():
        raise ValueError("GROQ_API_KEY is not set or is empty. Please set GROQ_API_KEY in .env.")

    logger.info(f"Initializing Groq LLM with model: {settings.GROQ_MODEL} (streaming={streaming})")

    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL,
        streaming=streaming,
        temperature=temperature,
        max_retries=max_retries,
    )
