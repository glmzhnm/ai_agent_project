"""Тонкий клиент к LLM.

Провайдер выбирается в конфиге. Работаем через httpx, а не через SDK: нужен
всего один вызов, зато полный контроль над таймаутами и обработкой ошибок.
"""

import asyncio

import httpx

from .config import Settings
from .errors import (
    NotConfiguredError,
    UpstreamError,
    UpstreamRateLimitError,
    UpstreamTimeoutError,
)

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
ANTHROPIC_VERSION = "2023-06-01"
# У моделей с внутренним рассуждением (gemini-3.x, o-series) часть бюджета уходит
# на скрытые reasoning-токены. 1200 не хватало: ответ обрывался на середине JSON.
MAX_TOKENS = 4000
RETRY_STATUSES = {429, 500, 502, 503, 529}


def _anthropic_payload(settings: Settings, system: str, user: str) -> dict:
    return {
        "model": settings.model,
        "max_tokens": MAX_TOKENS,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }


def _openai_payload(settings: Settings, system: str, user: str) -> dict:
    return {
        "model": settings.model,
        "max_tokens": MAX_TOKENS,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }


def _extract_text(provider: str, data: dict) -> str:
    if provider == "anthropic":
        blocks = data.get("content", [])
        return "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    choices = data.get("choices", [])
    if not choices:
        return ""
    return choices[0].get("message", {}).get("content", "") or ""


async def generate(settings: Settings, system: str, user: str) -> str:
    """Один вызов модели. Возвращает сырой текст ответа."""

    if not settings.is_configured:
        raise NotConfiguredError()

    url = settings.base_url
    if settings.provider == "anthropic":
        headers = {
            "x-api-key": settings.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        payload = _anthropic_payload(settings, system, user)
    else:
        # openai и gemini: у gemini OpenAI-совместимый эндпоинт, ключ тот же Bearer.
        headers = {
            "Authorization": f"Bearer {settings.api_key}",
            "content-type": "application/json",
        }
        payload = _openai_payload(settings, system, user)

    last_status = None
    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        for attempt in range(2):
            try:
                response = await client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException as exc:
                raise UpstreamTimeoutError() from exc
            except httpx.HTTPError as exc:
                raise UpstreamError("Не удалось соединиться с API модели.") from exc

            if response.status_code == 200:
                return _extract_text(settings.provider, response.json()).strip()

            last_status = response.status_code
            if response.status_code in (401, 403):
                raise NotConfiguredError("API-ключ отклонён провайдером модели.")
            if response.status_code not in RETRY_STATUSES or attempt == 1:
                break
            await asyncio.sleep(1.5)

    if last_status == 429:
        raise UpstreamRateLimitError()
    raise UpstreamError(f"API модели вернуло статус {last_status}.")
