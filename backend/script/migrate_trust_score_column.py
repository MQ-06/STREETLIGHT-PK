# backend/script/migrate_trust_score_column.py
"""
Migration script to add trust_score column to the reports table.
Records the Engine D trust score snapshot at the time of report creation.
"""
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys

# Add backend to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def run_migration():
    """Add trust_score column to reports table."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    # Create sync engine
    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            logger.info("Adding trust_score column to reports table...")

            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='reports' AND column_name='trust_score'
                    ) THEN
                        ALTER TABLE reports ADD COLUMN trust_score FLOAT;
                    END IF;
                END
                $$;
            """))

            logger.info("✅ Migration completed successfully!")

        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
