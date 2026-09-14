"""Доменные ошибки сервиса. Каждая знает свой HTTP-код и текст для пользователя."""


class AssistantError(Exception):
    status_code = 500
    default_message = "Внутренняя ошибка сервиса. Попробуйте ещё раз."

    def __init__(self, message: str | None = None):
        self.message = message or self.default_message
        super().__init__(self.message)


class Unauthorized(AssistantError):
    status_code = 401
    default_message = "Требуется вход. Войдите заново."


class NotConfiguredError(AssistantError):
    status_code = 503
    default_message = (
        "Модель не подключена: не задан API-ключ на сервере. "
        "Проверьте .env и перезапустите backend."
    )


class UpstreamTimeoutError(AssistantError):
    status_code = 504
    default_message = "Модель не ответила вовремя. Повторите запрос."


class UpstreamRateLimitError(AssistantError):
    status_code = 429
    default_message = "Слишком много запросов к модели. Подождите несколько секунд."


class UpstreamError(AssistantError):
    status_code = 502
    default_message = "Модель вернула ошибку. Повторите запрос чуть позже."
