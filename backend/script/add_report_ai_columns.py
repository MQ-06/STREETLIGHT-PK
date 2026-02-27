"""
Migration: Add AI Agent columns to reports table.
Run: python -m script.add_report_ai_columns
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from db.database import engine


def run_migration():
    columns = [
        ("validation_score", "FLOAT"),
        ("validation_status", "VARCHAR(20)"),
        ("validation_warnings", "TEXT"),
        ("ai_confidence", "FLOAT"),
        ("ai_predicted_class", "VARCHAR(50)"),
        ("ai_severity", "VARCHAR(20)"),
        ("final_score", "FLOAT"),
        ("gps_verified", "BOOLEAN DEFAULT FALSE"),
        ("gps_has_photo_location", "BOOLEAN DEFAULT FALSE"),
        ("gps_distance_km", "FLOAT"),
        ("gps_spoofing_detected", "BOOLEAN DEFAULT FALSE"),
    ]
    with engine.connect() as conn:
        for col_name, col_type in columns:
            try:
                conn.execute(text(
                    f"ALTER TABLE reports ADD COLUMN IF NOT EXISTS {col_name} {col_type}"
                ))
                conn.commit()
                print(f"  Added column: {col_name}")
            except Exception as e:
                if "already exists" in str(e).lower():
                    print(f"  Column {col_name} already exists, skipping")
                else:
                    raise
    print("Migration complete!")


if __name__ == "__main__":
    run_migration()
