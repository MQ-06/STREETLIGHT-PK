# backend/script/migrate_fcm_token.py
"""
Migration script to add fcm_token column to user_profiles table.
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
    """Add fcm_token column to user_profiles table."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env file")
        return

    # Create sync engine
    engine = create_engine(database_url, echo=False)

    with engine.begin() as conn:
        try:
            logger.info("Adding fcm_token column to user_profiles table...")
            
            # Use IF NOT EXISTS equivalent logic using a PL/pgSQL block
            conn.execute(text("""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 
                        FROM information_schema.columns 
                        WHERE table_name='user_profiles' AND column_name='fcm_token'
                    ) THEN
                        ALTER TABLE user_profiles ADD COLUMN fcm_token VARCHAR(255);
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
