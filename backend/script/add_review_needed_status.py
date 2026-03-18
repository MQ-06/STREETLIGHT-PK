from sqlalchemy import text

from db.database import engine


def migrate():
    """
    Migration: add REVIEW_NEEDED value to reportstatus enum.

    Safe to run multiple times thanks to IF NOT EXISTS.
    """
    ddl = "ALTER TYPE reportstatus ADD VALUE IF NOT EXISTS 'REVIEW_NEEDED';"

    with engine.begin() as conn:
        conn.execute(text(ddl))


if __name__ == "__main__":
    migrate()
    print("Migration complete: REVIEW_NEEDED added to reportstatus enum (if missing).")

