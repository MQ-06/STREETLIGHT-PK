import os
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

def check_columns():
    database_url = os.getenv("DATABASE_URL")
    engine = create_engine(database_url)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT table_schema, column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users'
            ORDER BY table_schema
        """))
        for row in result:
            logger.info(f"Schema: {row[0]} | Column: {row[1]}")

if __name__ == "__main__":
    check_columns()
