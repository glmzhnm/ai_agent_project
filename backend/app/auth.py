"""Пароли и JWT-сессии.

Логин закрывает доступ к сайту целиком, но не разграничивает данные:
история тикетов общая на всю команду. Поэтому здесь ровно то, что нужно
для гейта — хеш пароля и подпись/проверка токена, без ролей и разделения
видимости.
"""

import time

import bcrypt
import jwt
from fastapi import Cookie, Request

from .errors import Unauthorized

COOKIE_NAME = "session"
ALGORITHM = "HS256"
TOKEN_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 дней — внутренний инструмент, не банк


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Битый/чужого формата хеш — не роняем запрос, просто "неверный пароль".
        return False


def issue_token(user_id: int, login: str, secret: str) -> str:
    now = int(time.time())
    payload = {"user_id": user_id, "login": login, "iat": now, "exp": now + TOKEN_TTL_SECONDS}
    return jwt.encode(payload, secret, algorithm=ALGORITHM)


def decode_token(token: str, secret: str) -> dict:
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


class CurrentUser:
    def __init__(self, user_id: int, login: str):
        self.user_id = user_id
        self.login = login


def get_current_user(request: Request, session: str | None = Cookie(default=None)) -> CurrentUser:
    """FastAPI-зависимость: достаёт и проверяет JWT из cookie.

    401 без уточнений — истёк токен, подделан или просто отсутствует,
    для клиента разница не важна: во всех случаях это "войдите заново".
    """

    secret = request.app.state.settings.jwt_secret
    if not session:
        raise Unauthorized()
    try:
        payload = decode_token(session, secret)
    except jwt.PyJWTError:
        raise Unauthorized()
    return CurrentUser(user_id=payload["user_id"], login=payload["login"])
