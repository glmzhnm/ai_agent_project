-- Пользователи и общая история тикетов команды.

CREATE TABLE IF NOT EXISTS users (
    id            BIGSERIAL PRIMARY KEY,
    login         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tickets (
    id          BIGSERIAL PRIMARY KEY,
    author_id   BIGINT NOT NULL REFERENCES users(id),
    question    TEXT NOT NULL,
    mode        TEXT NOT NULL,
    answer      JSONB NOT NULL,
    meta        JSONB NOT NULL,
    escalate    BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS tickets_created_at_idx ON tickets (created_at DESC);
CREATE INDEX IF NOT EXISTS tickets_escalate_idx ON tickets (escalate) WHERE escalate = true;
