"""Контракты API: что принимаем от фронтенда и что возвращаем."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator


class Mode(str, Enum):
    """Роль, в которой отвечает ассистент."""

    engineer = "engineer"
    client = "client"
    escalation = "escalation"


class Risk(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: Mode = Mode.engineer

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Вопрос не может быть пустым")
        return cleaned


class Command(BaseModel):
    cmd: str
    why: str = ""


class Answer(BaseModel):
    """Структурированный ответ модели. Все поля кроме answer необязательны."""

    answer: str
    steps: list[str] = []
    commands: list[Command] = []
    risk: Risk = Risk.low
    escalate: bool = False
    escalate_reason: str = ""
    questions: list[str] = []
    tags: list[str] = []
    out_of_scope: bool = False

    @model_validator(mode="before")
    @classmethod
    def drop_nulls(cls, data):
        """Модель ставит null вместо пропуска поля. Это не ошибка, а "нечего сказать",
        поэтому null убираем и даём сработать значению по умолчанию."""

        if not isinstance(data, dict):
            return data
        return {k: v for k, v in data.items() if v is not None or k == "answer"}


class Meta(BaseModel):
    provider: str
    model: str
    mode: Mode
    latency_ms: int
    degraded: bool = False


class AskResponse(BaseModel):
    answer: Answer
    meta: Meta


class ErrorResponse(BaseModel):
    error: str
    detail: str = ""


class LoginRequest(BaseModel):
    login: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class MeResponse(BaseModel):
    login: str


class TicketOut(BaseModel):
    """Тикет из общей истории команды."""

    id: int
    question: str
    mode: Mode
    answer: Answer
    meta: Meta
    created_at: datetime


class TicketListResponse(BaseModel):
    items: list[TicketOut]
    limit: int
    offset: int
