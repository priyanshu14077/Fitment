"""Platform: API keys, usage rollups, idempotency records.

Revision ID: 0002
Revises: 0001
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # key_id is the public half of the key, used for the indexed lookup.
    # key_hash is SHA-256 of the secret half: 32 bytes, never the key itself.
    op.execute("""
        CREATE TABLE api_key (
            id         uuid        PRIMARY KEY DEFAULT gen_random_uuid(),
            key_id     text        NOT NULL UNIQUE,
            key_hash   bytea       NOT NULL CHECK (octet_length(key_hash) = 32),
            plan       text        NOT NULL CHECK (plan IN ('free', 'pro')),
            owner      text        NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            expires_at timestamptz,
            revoked_at timestamptz
        )
    """)
    op.execute("CREATE INDEX api_key_owner_idx ON api_key (owner)")

    # Written only by the flush task, which upserts per-minute Redis counts:
    # requests = usage_daily.requests + EXCLUDED.requests.
    op.execute("""
        CREATE TABLE usage_daily (
            api_key_id uuid   NOT NULL REFERENCES api_key (id) ON DELETE CASCADE,
            day        date   NOT NULL,
            endpoint   text   NOT NULL,
            requests   bigint NOT NULL DEFAULT 0,
            errors_4xx bigint NOT NULL DEFAULT 0,
            errors_5xx bigint NOT NULL DEFAULT 0,
            PRIMARY KEY (api_key_id, day, endpoint)
        )
    """)
    op.execute("CREATE INDEX usage_daily_day_idx ON usage_daily (day)")

    op.execute("""
        CREATE TABLE idempotency (
            api_key_id      uuid        NOT NULL REFERENCES api_key (id) ON DELETE CASCADE,
            idem_key        text        NOT NULL,
            request_hash    bytea       NOT NULL,
            status          text        NOT NULL CHECK (status IN ('in_progress', 'completed')),
            response_status smallint,
            response        jsonb,
            created_at      timestamptz NOT NULL DEFAULT now(),
            expires_at      timestamptz NOT NULL,
            PRIMARY KEY (api_key_id, idem_key)
        )
    """)
    op.execute("CREATE INDEX idempotency_expires_at_idx ON idempotency (expires_at)")


def downgrade() -> None:
    for table in ("idempotency", "usage_daily", "api_key"):
        op.execute(f"DROP TABLE {table}")
