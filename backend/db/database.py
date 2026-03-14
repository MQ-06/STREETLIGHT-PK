#backend/db/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os

# Load .env from backend directory so we use the same DB as migration scripts
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_backend_dir, ".env"))

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,    # drop & replace dead connections automatically
    pool_size=10,          # keep up to 10 persistent connections
    max_overflow=20,       # allow up to 20 extra on burst
    pool_recycle=1800,     # recycle connections every 30 min (before Supabase drops them)
)
Base= declarative_base()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        return str(e)
    