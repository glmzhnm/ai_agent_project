"""Сценарий "задать вопрос": собрать промпт, вызвать модель, разобрать ответ.

Модель иногда возвращает JSON внутри markdown или с лишним текстом вокруг.
Поэтому разбор идёт в три ступени: чистый парсинг, попытка починки вторым
вызовом, и в самом конце деградация до обычного текста. Сервис не падает
никогда, максимум отдаёт ответ попроще с флагом degraded.
"""

import json
import time

from pydantic import ValidationError

from ..config import Settings
from ..llm_client import generate
from ..prompts import REPAIR_INSTRUCTION, build_system_prompt, build_user_prompt
from ..schemas import Answer, AskResponse, Meta, Mode


def _strip_code_fence(text: str) -> str:
    cleaned = text.strip()
    if not cleaned.startswith("```"):
        return cleaned
    lines = cleaned.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _slice_json_object(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return text
    return text[start : end + 1]


def parse_answer(raw: str) -> Answer | None:
    """Пробует превратить сырой текст модели в Answer. None, если не вышло."""

    candidate = _slice_json_object(_strip_code_fence(raw))
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    try:
        return Answer.model_validate(data)
    except ValidationError:
        return None


def _fallback_answer(raw: str) -> Answer:
    """Модель ответила текстом. Показываем текст, но честно помечаем деградацию."""

    text = _strip_code_fence(raw) or "Модель вернула пустой ответ. Повторите запрос."
    return Answer(answer=text)


async def ask(settings: Settings, question: str, mode: Mode) -> AskResponse:
    started = time.perf_counter()
    system = build_system_prompt(mode)

    raw = await generate(settings, system, build_user_prompt(question))
    answer = parse_answer(raw)
    degraded = False

    if answer is None:
        repair_user = f"{REPAIR_INSTRUCTION}\n\nИсходный ответ:\n{raw}"
        raw_repaired = await generate(settings, system, repair_user)
        answer = parse_answer(raw_repaired)
        if answer is None:
            answer = _fallback_answer(raw)
            degraded = True

    return AskResponse(
        answer=answer,
        meta=Meta(
            provider=settings.provider,
            model=settings.model,
            mode=mode,
            latency_ms=int((time.perf_counter() - started) * 1000),
            degraded=degraded,
        ),
    )
