"""
Migration: Layer 3 Community Verification tables
=================================================
Creates two new tables and adds new columns to existing tables required
by Engine C (Community Verification).

New tables
----------
    verification_requests  — one row per report queued for community review
    verification_votes     — one vote row per (user, request) pair

New columns on existing tables
-------------------------------
    reports.community_score         FLOAT  NULL
    user_profiles.last_known_lat    FLOAT  NULL
    user_profiles.last_known_lng    FLOAT  NULL

Safe to re-run — every statement uses IF NOT EXISTS / DO-NOTHING logic.

Run from the backend/ directory:
    python -m script.migrate_verification_tables
"""

import sys
import os
import logging

# ── Ensure `backend/` is on the path so db.database resolves correctly ──────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from db.database import engine

# ── Logging setup ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Migration steps ────────────────────────────────────────────────────────
#
# Each entry is (description, raw_sql).
# Statements use IF NOT EXISTS / DO NOTHING so the script is idempotent.
# Named constraints are guarded with information_schema lookups so Postgres
# won't duplicate them on repeated runs.
# ──────────────────────────────────────────────────────────────────────────
STEPS = [
    # ── 1. Enum type: verificationstatus ──────────────────────────────────
    (
        "enum type  verificationstatus  ('PENDING', 'COMPLETED', 'EXPIRED')",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'verificationstatus'
            ) THEN
                CREATE TYPE verificationstatus AS ENUM ('PENDING', 'COMPLETED', 'EXPIRED');
            END IF;
        END
        $$
        """,
    ),

    # ── 2. Enum type: votechoice ───────────────────────────────────────────
    (
        "enum type  votechoice  ('YES', 'NO')",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'votechoice'
            ) THEN
                CREATE TYPE votechoice AS ENUM ('YES', 'NO');
            END IF;
        END
        $$
        """,
    ),

    # ── 3. Table: verification_requests ───────────────────────────────────
    (
        "table  verification_requests",
        """
        CREATE TABLE IF NOT EXISTS verification_requests (
            id              SERIAL          PRIMARY KEY,
            report_id       INTEGER         NOT NULL UNIQUE
                                            REFERENCES reports(id) ON DELETE CASCADE,
            status          verificationstatus  NOT NULL DEFAULT 'PENDING',
            radius_m        FLOAT           NOT NULL DEFAULT 500.0,
            min_votes       INTEGER         NOT NULL DEFAULT 3,
            timeout_hours   INTEGER         NOT NULL DEFAULT 48,
            community_score FLOAT,
            total_votes     INTEGER         NOT NULL DEFAULT 0,
            yes_votes       INTEGER         NOT NULL DEFAULT 0,
            no_votes        INTEGER         NOT NULL DEFAULT 0,
            created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
            completed_at    TIMESTAMPTZ
        )
        """,
    ),

    # ── 4. Table: verification_votes ──────────────────────────────────────
    (
        "table  verification_votes",
        """
        CREATE TABLE IF NOT EXISTS verification_votes (
            id          SERIAL      PRIMARY KEY,
            request_id  INTEGER     NOT NULL
                                    REFERENCES verification_requests(id) ON DELETE CASCADE,
            user_id     INTEGER     NOT NULL
                                    REFERENCES users(id) ON DELETE CASCADE,
            vote        votechoice  NOT NULL,
            weight      FLOAT       NOT NULL DEFAULT 1.0,
            distance_m  FLOAT,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            CONSTRAINT  uq_vv_request_user UNIQUE (request_id, user_id)
        )
        """,
    ),

    # ── 5. reports.community_score ────────────────────────────────────────
    (
        "reports.community_score  FLOAT NULL",
        """
        ALTER TABLE reports
            ADD COLUMN IF NOT EXISTS community_score
            FLOAT
        """,
    ),

    # ── 6. user_profiles.last_known_lat ───────────────────────────────────
    (
        "user_profiles.last_known_lat  FLOAT NULL",
        """
        ALTER TABLE user_profiles
            ADD COLUMN IF NOT EXISTS last_known_lat
            FLOAT
        """,
    ),

    # ── 7. user_profiles.last_known_lng ───────────────────────────────────
    (
        "user_profiles.last_known_lng  FLOAT NULL",
        """
        ALTER TABLE user_profiles
            ADD COLUMN IF NOT EXISTS last_known_lng
            FLOAT
        """,
    ),
]


# ── Runner ─────────────────────────────────────────────────────────────────
def run_migration() -> None:
    logger.info("=" * 60)
    logger.info("🚀 Starting migration: Layer 3 Community Verification tables")
    logger.info("=" * 60)

    with engine.connect() as conn:
        for i, (description, sql) in enumerate(STEPS, start=1):
            logger.info(f"🔧 Step {i}/{len(STEPS)}: {description}")
            try:
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"   ✅ Done")
            except Exception as exc:
                err = str(exc).lower()
                if "already exists" in err:
                    # IF NOT EXISTS should prevent this, but guard anyway
                    logger.info(f"   ⏭️  Already exists — skipped")
                    conn.rollback()
                else:
                    logger.error(f"   ❌ FAILED: {exc}")
                    raise

    logger.info("=" * 60)
    logger.info("✅ Migration complete — all community verification tables are in place.")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_migration()
