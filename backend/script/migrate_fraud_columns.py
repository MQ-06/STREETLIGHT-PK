"""
Migration: Layer 2 Fraud Detection columns
==========================================
Adds two new columns to the `reports` table required by Engine B.

    is_flagged_for_spam  BOOLEAN  NOT NULL  DEFAULT false
    duplicate_of_id      INTEGER  NULL      REFERENCES reports(id) ON DELETE SET NULL

Safe to re-run — every statement uses IF NOT EXISTS / DO-NOTHING logic.

Run from the backend/ directory:
    python -m script.migrate_fraud_columns
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
# The FK constraint is added as a named constraint so Postgres won't
# duplicate it on repeated runs.
# ──────────────────────────────────────────────────────────────────────────
STEPS = [
    (
        "is_flagged_for_spam  BOOLEAN NOT NULL DEFAULT false",
        """
        ALTER TABLE reports
            ADD COLUMN IF NOT EXISTS is_flagged_for_spam
            BOOLEAN NOT NULL DEFAULT false
        """,
    ),
    (
        "duplicate_of_id  INTEGER REFERENCES reports(id) ON DELETE SET NULL",
        """
        ALTER TABLE reports
            ADD COLUMN IF NOT EXISTS duplicate_of_id
            INTEGER
        """,
    ),
    (
        "FK constraint  fk_reports_duplicate_of_id → reports(id)",
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM   information_schema.table_constraints
                WHERE  constraint_name = 'fk_reports_duplicate_of_id'
                AND    table_name      = 'reports'
            ) THEN
                ALTER TABLE reports
                    ADD CONSTRAINT fk_reports_duplicate_of_id
                    FOREIGN KEY (duplicate_of_id)
                    REFERENCES reports (id)
                    ON DELETE SET NULL;
            END IF;
        END
        $$
        """,
    ),
]


# ── Runner ─────────────────────────────────────────────────────────────────
def run_migration() -> None:
    logger.info("=" * 60)
    logger.info("🚀 Starting migration: Layer 2 Fraud Detection columns")
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
    logger.info("✅ Migration complete — all fraud detection columns are in place.")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_migration()
