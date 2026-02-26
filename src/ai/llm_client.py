from __future__ import annotations

from groq import Groq

from src.config import settings

_client: Groq | None = None


def get_groq_client() -> Groq:
    global _client

    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is missing. Set it in .env or environment variables.")
        _client = Groq(api_key=settings.groq_api_key)

    return _client
