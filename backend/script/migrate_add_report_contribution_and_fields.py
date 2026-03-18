from sqlalchemy import text

from db.database import engine


def migrate():
    """
    Migration: add report_contributions table and new fields on reports.

    - Creates report_contributions table if it does not already exist.
    - Adds reports.confirmation_count (INT, default 0) if missing.
    - Adds reports.best_image_url (VARCHAR) if missing.
    - Adds missing AI / GPS / fraud / scoring columns on reports (idempotent).

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

        -- 4) Ensure AI/GPS/fraud/scoring columns exist (models evolved over time)

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'validation_score'
        ) THEN
            ALTER TABLE reports ADD COLUMN validation_score DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'validation_status'
        ) THEN
            ALTER TABLE reports ADD COLUMN validation_status VARCHAR(20);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'validation_warnings'
        ) THEN
            ALTER TABLE reports ADD COLUMN validation_warnings TEXT;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'ai_confidence'
        ) THEN
            ALTER TABLE reports ADD COLUMN ai_confidence DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'ai_predicted_class'
        ) THEN
            ALTER TABLE reports ADD COLUMN ai_predicted_class VARCHAR(50);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'ai_severity'
        ) THEN
            ALTER TABLE reports ADD COLUMN ai_severity VARCHAR(20);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'final_score'
        ) THEN
            ALTER TABLE reports ADD COLUMN final_score DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'image_hash'
        ) THEN
            ALTER TABLE reports ADD COLUMN image_hash VARCHAR(128);
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'gps_verified'
        ) THEN
            ALTER TABLE reports ADD COLUMN gps_verified BOOLEAN NOT NULL DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'gps_has_photo_location'
        ) THEN
            ALTER TABLE reports ADD COLUMN gps_has_photo_location BOOLEAN NOT NULL DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'gps_distance_km'
        ) THEN
            ALTER TABLE reports ADD COLUMN gps_distance_km DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'gps_spoofing_detected'
        ) THEN
            ALTER TABLE reports ADD COLUMN gps_spoofing_detected BOOLEAN NOT NULL DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'is_flagged_for_spam'
        ) THEN
            ALTER TABLE reports ADD COLUMN is_flagged_for_spam BOOLEAN NOT NULL DEFAULT FALSE;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'duplicate_of_id'
        ) THEN
            ALTER TABLE reports ADD COLUMN duplicate_of_id INTEGER;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'community_score'
        ) THEN
            ALTER TABLE reports ADD COLUMN community_score DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'trust_score'
        ) THEN
            ALTER TABLE reports ADD COLUMN trust_score DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'combined_score'
        ) THEN
            ALTER TABLE reports ADD COLUMN combined_score DOUBLE PRECISION;
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'reports' AND column_name = 'verification_status'
        ) THEN
            ALTER TABLE reports ADD COLUMN verification_status VARCHAR(20) DEFAULT 'PENDING';
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

