"""Конфигурация сервиса. Читается из окружения один раз при старте."""

import os
from dataclasses import dataclass
from functools import lru_cache

DEFAULT_MODELS = {
    "anthropic": "claude-sonnet-5",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-3.6-flash",
    "groq": "openai/gpt-oss-120b",
}

DEFAULT_BASE_URLS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
    "groq": "https://api.groq.com/openai/v1/chat/completions",
}

API_KEY_VARS = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
}


@dataclass(frozen=True)
class Settings:
    provider: str
    api_key: str
    model: str
    base_url: str
    timeout_seconds: float
    max_question_chars: int
    allowed_origins: tuple[str, ...]
    database_url: str
    jwt_secret: str

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


@lru_cache
def get_settings() -> Settings:
    provider = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    if provider not in DEFAULT_MODELS:
        provider = "anthropic"

    raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173")

    return Settings(
        provider=provider,
        api_key=os.getenv(API_KEY_VARS[provider], "").strip(),
        model=os.getenv("LLM_MODEL", DEFAULT_MODELS[provider]).strip(),
        base_url=os.getenv("LLM_BASE_URL", DEFAULT_BASE_URLS[provider]).strip(),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "45")),
        max_question_chars=int(os.getenv("MAX_QUESTION_CHARS", "1500")),
        allowed_origins=tuple(o.strip() for o in raw_origins.split(",") if o.strip()),
        database_url=os.getenv(
            "DATABASE_URL", "postgresql://assistant:assistant@localhost:5432/assistant"
        ).strip(),
        jwt_secret=os.getenv("JWT_SECRET", "").strip(),
    )