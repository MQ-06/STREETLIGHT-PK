"""
Migration script to add role column to users table.
"""
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Add backend to Python path
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
            logger.info("Adding role column to users table...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='users' AND column_name='role'
                    ) THEN
                        ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'citizen';
                    END IF;
                END
                $$;
            """))

            conn.execute(text("""
                UPDATE users
                SET role = 'citizen'
                WHERE role IS NULL OR role = '';
            """))

            logger.info("✅ Migration completed successfully!")
        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
