"""Хранение и чтение тикетов. История общая на всю команду."""

import json

import asyncpg

from ..schemas import Answer, Meta, Mode, TicketOut


async def insert_ticket(
    pool: asyncpg.Pool, author_id: int, question: str, mode: Mode, answer: Answer, meta: Meta
) -> TicketOut:
    row = await pool.fetchrow(
        """
        INSERT INTO tickets (author_id, question, mode, answer, meta, escalate)
        VALUES ($1, $2, $3, $4::jsonb, $5::jsonb, $6)
        RETURNING id, question, mode, answer, meta, escalate, created_at
        """,
        author_id,
        question,
        mode.value,
        json.dumps(answer.model_dump(mode="json")),
        json.dumps(meta.model_dump(mode="json")),
        answer.escalate,
    )
    return _row_to_ticket(row)


async def list_tickets(pool: asyncpg.Pool, limit: int, offset: int, q: str | None) -> list[TicketOut]:
    if q:
        rows = await pool.fetch(
            """
            SELECT id, question, mode, answer, meta, escalate, created_at
            FROM tickets
            WHERE question ILIKE $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
            """,
            f"%{q}%",
            limit,
            offset,
        )
    else:
        rows = await pool.fetch(
            """
            SELECT id, question, mode, answer, meta, escalate, created_at
            FROM tickets
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )
    return [_row_to_ticket(row) for row in rows]


def _row_to_ticket(row: asyncpg.Record) -> TicketOut:
    return TicketOut(
        id=row["id"],
        question=row["question"],
        mode=row["mode"],
        answer=json.loads(row["answer"]),
        meta=json.loads(row["meta"]),
        created_at=row["created_at"],
    )
