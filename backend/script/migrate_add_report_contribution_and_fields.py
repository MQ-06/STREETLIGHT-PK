from sqlalchemy import text

from db.database import engine


def migrate():
    """
    Migration: add report_contributions table and new fields on reports.

    - Creates report_contributions table if it does not already exist.
    - Adds reports.confirmation_count (INT, default 0) if missing.
    - Adds reports.best_image_url (VARCHAR) if missing.

    This migration is idempotent and safe to run multiple times.
    """
    ddl = """
    DO $$
    BEGIN
        -- 1) Create report_contributions table if missing
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'report_contributions'
        ) THEN
            CREATE TABLE report_contributions (
                id SERIAL PRIMARY KEY,
                report_id INTEGER NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                image_url VARCHAR NOT NULL,
                ai_confidence DOUBLE PRECISION,
                ai_severity VARCHAR(20),
                location_lat DOUBLE PRECISION,
                location_lng DOUBLE PRECISION,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        END IF;

        -- 2) Add confirmation_count column to reports if missing
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'reports'
              AND column_name = 'confirmation_count'
        ) THEN
            ALTER TABLE reports
            ADD COLUMN confirmation_count INTEGER NOT NULL DEFAULT 0;
        END IF;

        -- 3) Add best_image_url column to reports if missing
        IF NOT EXISTS (
            SELECT 1
            FROM information_schema.columns
            WHERE table_name = 'reports'
              AND column_name = 'best_image_url'
        ) THEN
            ALTER TABLE reports
            ADD COLUMN best_image_url VARCHAR;
        END IF;
    END;
    $$;
    """

    with engine.begin() as conn:
        conn.execute(text(ddl))


if __name__ == "__main__":
    migrate()
    print(
        "Migration complete: report_contributions table and "
        "reports.confirmation_count / reports.best_image_url ensured."
    )

