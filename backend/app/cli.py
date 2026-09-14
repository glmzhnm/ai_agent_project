"""Команды администрирования. Единственный способ завести пользователя —
публичной регистрации в этом сервисе нет.

Использование:
    python -m app.cli create-user --login ivan
"""

import argparse
import asyncio
import getpass

from dotenv import load_dotenv

load_dotenv()

from .auth import hash_password  # noqa: E402
from .config import get_settings  # noqa: E402
from .db import create_pool  # noqa: E402


async def create_user(login: str, password: str) -> None:
    settings = get_settings()
    pool = await create_pool(settings.database_url)  # заодно применяет миграции
    try:
        existing = await pool.fetchval("SELECT id FROM users WHERE login = $1", login)
        if existing is not None:
            raise SystemExit(f"Пользователь '{login}' уже существует.")
        await pool.execute(
            "INSERT INTO users (login, password_hash) VALUES ($1, $2)",
            login,
            hash_password(password),
        )
    finally:
        await pool.close()
    print(f"Пользователь '{login}' создан.")


def main() -> None:
    parser = argparse.ArgumentParser(prog="app.cli")
    sub = parser.add_subparsers(dest="command", required=True)

    create = sub.add_parser("create-user", help="Завести нового пользователя")
    create.add_argument("--login", required=True)

    args = parser.parse_args()

    if args.command == "create-user":
        password = getpass.getpass("Пароль: ")
        confirm = getpass.getpass("Повторите пароль: ")
        if password != confirm:
            raise SystemExit("Пароли не совпадают.")
        if not password:
            raise SystemExit("Пароль не может быть пустым.")
        asyncio.run(create_user(args.login, password))


if __name__ == "__main__":
    main()
