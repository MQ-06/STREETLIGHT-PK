"""
Migration: In-app notifications table
====================================

Creates a `notifications` table to support (DB-backed notifications).
Safe to re-run (idempotent).

Fields:
  - user_id (FK users.id)
  - type/title/body
  - entity_type/entity_id (optional deep link)
  - data (JSON)
  - dedupe_key (unique) to prevent duplicate events
  - created_at / read_at
"""

import logging

from sqlalchemy import text

from db.database import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_migration() -> None:
    ddl = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'notifications'
        ) THEN
            CREATE TABLE notifications (
                id          SERIAL      PRIMARY KEY,
                user_id     INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                type        VARCHAR(50) NOT NULL,
                title       VARCHAR(200) NOT NULL,
                body        TEXT,
                entity_type VARCHAR(50),
                entity_id   INTEGER,
                data        JSONB,
                dedupe_key  VARCHAR(200),
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                read_at     TIMESTAMPTZ
            );

            CREATE INDEX ix_notifications_user_id_created_at
                ON notifications (user_id, created_at DESC);
            CREATE INDEX ix_notifications_user_id_read_at
                ON notifications (user_id, read_at);
            CREATE INDEX ix_notifications_type
                ON notifications (type);
            CREATE INDEX ix_notifications_entity
                ON notifications (entity_type, entity_id);
        END IF;

        -- Add dedupe_key unique constraint if missing
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints tc
            WHERE tc.table_name = 'notifications'
              AND tc.constraint_type = 'UNIQUE'
              AND tc.constraint_name = 'uq_notifications_dedupe_key'
        ) THEN
            ALTER TABLE notifications
            ADD CONSTRAINT uq_notifications_dedupe_key UNIQUE (dedupe_key);
        END IF;

    END;
    $$;
    """

    logger.info("🔔 Starting migration: notifications table")
    with engine.begin() as conn:
        conn.execute(text(ddl))
    logger.info("✅ Migration complete: notifications table ensured")


if __name__ == "__main__":
    run_migration()

