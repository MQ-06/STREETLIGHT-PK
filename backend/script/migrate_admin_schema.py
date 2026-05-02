"""
Migration: Admin schema — Phase 1
==================================
Creates 3 new tables and adds 5 new columns to the reports table.

New tables:
  - routing_table        city+department → officer mapping
  - report_logs          immutable audit trail for every report transition
  - field_worker_tokens  72-hour single-use tokens for field workers

New columns on reports:
  - assigned_city … kanban_stage (Phase 1)
  - after_image_* , citizen_* , resolution_notified_at , auto_resolve_at ,
    blockchain_* , closed_at (resolution flow — aligns ORM with older DBs)

Safe to re-run — all operations are idempotent (IF NOT EXISTS / DO $$ guards).
"""

import logging
import os
import sys

from sqlalchemy import text

# Allow running as a standalone script from the backend/ directory
_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)

from db.database import engine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


DDL = """
DO $$
BEGIN

    -- ================================================================
    -- 1. routing_table
    -- ================================================================
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'routing_table'
    ) THEN
        CREATE TABLE routing_table (
            id               SERIAL       PRIMARY KEY,
            city             VARCHAR(50)  NOT NULL,
            department       VARCHAR(50)  NOT NULL,
            department_name  VARCHAR(200) NOT NULL,
            officer_id       INTEGER      NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
            created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE (city, department)
        );

        CREATE INDEX ix_routing_table_city       ON routing_table (city);
        CREATE INDEX ix_routing_table_department ON routing_table (department);
        RAISE NOTICE 'Created table: routing_table';
    ELSE
        RAISE NOTICE 'Table already exists: routing_table';
    END IF;


    -- ================================================================
    -- 2. report_logs
    -- ================================================================
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'report_logs'
    ) THEN
        CREATE TABLE report_logs (
            id                   SERIAL        PRIMARY KEY,
            report_id            INTEGER       NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            changed_by           VARCHAR(100)  NOT NULL,
            previous_stage       VARCHAR(50),
            new_stage            VARCHAR(50),
            previous_status      VARCHAR(50),
            new_status           VARCHAR(50),
            assigned_city        VARCHAR(50),
            assigned_department  VARCHAR(50),
            assigned_officer_id  INTEGER       REFERENCES users(id) ON DELETE SET NULL,
            note                 TEXT,
            ai_managed           BOOLEAN       NOT NULL DEFAULT FALSE,
            created_at           TIMESTAMPTZ   NOT NULL DEFAULT NOW()
        );

        CREATE INDEX ix_report_logs_report_id   ON report_logs (report_id);
        CREATE INDEX ix_report_logs_created_at  ON report_logs (created_at DESC);
        CREATE INDEX ix_report_logs_ai_managed  ON report_logs (ai_managed);
        RAISE NOTICE 'Created table: report_logs';
    ELSE
        RAISE NOTICE 'Table already exists: report_logs';
    END IF;


    -- ================================================================
    -- 3. field_worker_tokens
    -- ================================================================
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_name = 'field_worker_tokens'
    ) THEN
        CREATE TABLE field_worker_tokens (
            id                      SERIAL       PRIMARY KEY,
            token                   VARCHAR(64)  NOT NULL UNIQUE,
            report_id               INTEGER      NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
            created_by_officer_id   INTEGER      NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            expires_at              TIMESTAMPTZ  NOT NULL,
            used                    BOOLEAN      NOT NULL DEFAULT FALSE,
            used_at                 TIMESTAMPTZ,
            after_photo_url         VARCHAR(500),
            verification_result     VARCHAR(20),
            verification_note       VARCHAR(500),
            created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );

        CREATE INDEX ix_field_worker_tokens_token     ON field_worker_tokens (token);
        CREATE INDEX ix_field_worker_tokens_report_id ON field_worker_tokens (report_id);
        RAISE NOTICE 'Created table: field_worker_tokens';
    ELSE
        RAISE NOTICE 'Table already exists: field_worker_tokens';
    END IF;


    -- ================================================================
    -- 4. New columns on reports
    -- ================================================================

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'assigned_city'
    ) THEN
        ALTER TABLE reports ADD COLUMN assigned_city VARCHAR(50);
        RAISE NOTICE 'Added column: reports.assigned_city';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'assigned_department'
    ) THEN
        ALTER TABLE reports ADD COLUMN assigned_department VARCHAR(50);
        RAISE NOTICE 'Added column: reports.assigned_department';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'assigned_officer_id'
    ) THEN
        ALTER TABLE reports ADD COLUMN assigned_officer_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added column: reports.assigned_officer_id';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'assigned_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN assigned_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.assigned_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'kanban_stage'
    ) THEN
        ALTER TABLE reports ADD COLUMN kanban_stage VARCHAR(30) DEFAULT 'NEW';
        RAISE NOTICE 'Added column: reports.kanban_stage';
    END IF;


    -- ================================================================
    -- 4b. Resolution / citizen feedback / blockchain (ORM parity)
    -- ================================================================

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'after_image_url'
    ) THEN
        ALTER TABLE reports ADD COLUMN after_image_url VARCHAR(2048);
        RAISE NOTICE 'Added column: reports.after_image_url';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'after_image_uploaded_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN after_image_uploaded_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.after_image_uploaded_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'after_image_uploaded_by'
    ) THEN
        ALTER TABLE reports ADD COLUMN after_image_uploaded_by INTEGER REFERENCES users(id) ON DELETE SET NULL;
        RAISE NOTICE 'Added column: reports.after_image_uploaded_by';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'citizen_response'
    ) THEN
        ALTER TABLE reports ADD COLUMN citizen_response VARCHAR(20);
        RAISE NOTICE 'Added column: reports.citizen_response';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'citizen_confirmed_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN citizen_confirmed_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.citizen_confirmed_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'resolution_notified_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN resolution_notified_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.resolution_notified_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'auto_resolve_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN auto_resolve_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.auto_resolve_at';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'blockchain_resolve_tx'
    ) THEN
        ALTER TABLE reports ADD COLUMN blockchain_resolve_tx VARCHAR(100);
        RAISE NOTICE 'Added column: reports.blockchain_resolve_tx';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'blockchain_status'
    ) THEN
        ALTER TABLE reports ADD COLUMN blockchain_status VARCHAR(20);
        RAISE NOTICE 'Added column: reports.blockchain_status';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'reports' AND column_name = 'closed_at'
    ) THEN
        ALTER TABLE reports ADD COLUMN closed_at TIMESTAMPTZ;
        RAISE NOTICE 'Added column: reports.closed_at';
    END IF;


    -- ================================================================
    -- 5. city column on users (for city_admin scope)
    -- ================================================================
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'city'
    ) THEN
        ALTER TABLE users ADD COLUMN city VARCHAR(50);
        RAISE NOTICE 'Added column: users.city';
    END IF;

END;
$$;
"""


def run_migration() -> None:
    logger.info("🏗️  Starting migration: admin schema (Phase 1)")
    with engine.begin() as conn:
        conn.execute(text(DDL))
    logger.info("✅ Migration complete: admin schema ensured")


if __name__ == "__main__":
    run_migration()
