# backend/script/migrate_comments.py
"""
Migration script to create the comments table.

Run from the backend/ directory:
    python -m script.migrate_comments
"""
import logging
import os
import sys

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def run_migration():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            logger.info("Creating comments table if not exists...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS public.comments (
                    id          SERIAL PRIMARY KEY,
                    report_id   INTEGER NOT NULL REFERENCES public.reports(id) ON DELETE CASCADE,
                    user_id     INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
                    text        TEXT NOT NULL,
                    created_at  TIMESTAMPTZ DEFAULT NOW()
                );
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_comments_report_id
                    ON public.comments (report_id);
            """))
            logger.info("✅ Migration complete: comments table ready")
        except Exception as e:
            logger.error(f"❌ Migration error: {e}")
            raise


if __name__ == "__main__":
    run_migration()
