# backend/script/migrate_final_score.py
"""
Migration script to add Step 5 final confidence score columns to the reports table.
  - reports.combined_score      FLOAT        (weighted AI + community + trust score)
  - reports.verification_status VARCHAR(20)  (AUTO_VERIFIED | REVIEW_NEEDED | REJECTED | PENDING)
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
    """Add combined_score and verification_status columns to reports table."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    # Create sync engine
    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            # Step 1: Add combined_score
            logger.info("Adding combined_score column to reports table...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='reports' AND column_name='combined_score'
                    ) THEN
                        ALTER TABLE reports ADD COLUMN combined_score FLOAT;
                    END IF;
                END
                $$;
            """))
            logger.info("✅ Step 1 complete: reports.combined_score ready")

            # Step 2: Add verification_status
            logger.info("Adding verification_status column to reports table...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='reports' AND column_name='verification_status'
                    ) THEN
                        ALTER TABLE reports ADD COLUMN verification_status VARCHAR(20) DEFAULT 'PENDING';
                    END IF;
                END
                $$;
            """))
            logger.info("✅ Step 2 complete: reports.verification_status ready")

            logger.info("✅ Migration completed successfully!")

        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
