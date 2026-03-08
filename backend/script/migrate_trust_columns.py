# backend/script/migrate_trust_columns.py
"""
Migration script to add Engine D trust scoring columns:
  - users.created_at       TIMESTAMPTZ  (account age for trust scoring)
  - user_profiles.fraud_flags  INTEGER  (cumulative fraud detection count)
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
    """Add trust scoring columns to users and user_profiles tables."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    # Create sync engine
    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            # Step 1: Add created_at to users
            logger.info("Adding created_at column to users table...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='users' AND column_name='created_at'
                    ) THEN
                        ALTER TABLE users ADD COLUMN created_at TIMESTAMPTZ DEFAULT NOW();
                    END IF;
                END
                $$;
            """))
            logger.info("✅ Step 1 complete: users.created_at ready")

            # Step 2: Add fraud_flags to user_profiles
            logger.info("Adding fraud_flags column to user_profiles table...")
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1
                        FROM information_schema.columns
                        WHERE table_name='user_profiles' AND column_name='fraud_flags'
                    ) THEN
                        ALTER TABLE user_profiles ADD COLUMN fraud_flags INTEGER DEFAULT 0;
                    END IF;
                END
                $$;
            """))
            logger.info("✅ Step 2 complete: user_profiles.fraud_flags ready")

            logger.info("✅ Migration completed successfully!")

        except Exception as e:
            logger.error(f"❌ Error during migration: {str(e)}")
            raise e


if __name__ == "__main__":
    run_migration()
