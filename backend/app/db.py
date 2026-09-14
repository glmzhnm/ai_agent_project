"""Пул соединений с Postgres и раннер миграций.

Миграции — простые пронумерованные .sql файлы в backend/migrations.
Никакого Alembic: для двух таблиц это лишний слой. Раннер сам создаёт
служебную таблицу schema_migrations и применяет ещё не применённые файлы
по порядку при каждом старте — повторный запуск ничего не делает.
"""

import pathlib

import asyncpg

MIGRATIONS_DIR = pathlib.Path(__file__).resolve().parent.parent / "migrations"


async def run_migrations(pool: asyncpg.Pool) -> None:
    async with pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version    TEXT PRIMARY KEY,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )
            """
        )
        applied = {row["version"] for row in await conn.fetch("SELECT version FROM schema_migrations")}

        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            if path.name in applied:
                continue
            sql = path.read_text()
            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (version) VALUES ($1)", path.name
                )


async def create_pool(database_url: str) -> asyncpg.Pool:
    pool = await asyncpg.create_pool(database_url, min_size=1, max_size=5)
    await run_migrations(pool)
    return pool
