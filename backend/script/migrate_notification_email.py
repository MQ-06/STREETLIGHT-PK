"""
Migration: add notification_email column to users table.

Safe to re-run (idempotent).

Usage:
    cd backend
    python script/migrate_notification_email.py
"""
import logging
import os
import sys

from sqlalchemy import text

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)

from db.database import engine

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)


DDL = """
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'notification_email'
    ) THEN
        ALTER TABLE users ADD COLUMN notification_email VARCHAR(255);
        RAISE NOTICE 'Added column: users.notification_email';
    ELSE
        RAISE NOTICE 'Column already exists: users.notification_email';
    END IF;
END;
$$;
"""


def run():
    logger.info("Starting migration: notification_email column")
    with engine.begin() as conn:
        conn.execute(text(DDL))
    logger.info("Migration complete.")


if __name__ == "__main__":
    run()
