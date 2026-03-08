"""
Migration script to add role column to users table.
"""
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Add backend to Python path and load .env from backend directory
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)
_env_path = os.path.join(_backend_dir, ".env")
load_dotenv(_env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_migration():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    # Log which DB we're touching (mask password)
    try:
        from urllib.parse import urlparse
        p = urlparse(database_url)
        logger.info("Database: %s@%s%s", p.username, p.hostname or "", p.path or "")
    except Exception:
        pass

    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            # Target public.users explicitly (same schema the app uses)
            logger.info("Adding role column to public.users...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = 'users'
                          AND column_name = 'role'
                    ) THEN
                        ALTER TABLE public.users
                        ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'citizen';
                    END IF;
                END
                $$;
            """))

            # Verify: list columns of public.users
            rows = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = 'users'
                ORDER BY ordinal_position
            """)).fetchall()
            columns = [r[0] for r in rows]
            logger.info("public.users columns: %s", columns)
            if "role" not in columns:
                raise RuntimeError("Column 'role' still missing after migration. Check schema and DB.")

            logger.info("✅ Migration completed successfully!")
        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
