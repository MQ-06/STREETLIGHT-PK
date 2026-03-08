"""
Seed 4 hardcoded admin users (one per admin role).
Run once from backend: python script/seed_admin_users.py

All use password: Admin@123
"""
import logging
import os
import sys
from datetime import datetime, timezone

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

_backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _backend_dir)
load_dotenv(os.path.join(_backend_dir, ".env"))

from utils.auth import hash_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared password for all 4 admin accounts
ADMIN_PASSWORD = "Admin@123"

HARDCODED_ADMINS = [
    {
        "email": "municipal_officer@streetlight.local",
        "first_name": "Municipal",
        "last_name": "Officer",
        "cnic": "1111111111111",
        "role": "municipal_officer",
    },
    {
        "email": "department_head@streetlight.local",
        "first_name": "Department",
        "last_name": "Head",
        "cnic": "2222222222222",
        "role": "department_head",
    },
    {
        "email": "city_planner@streetlight.local",
        "first_name": "City",
        "last_name": "Planner",
        "cnic": "3333333333333",
        "role": "city_planner",
    },
    {
        "email": "system_admin@streetlight.local",
        "first_name": "System",
        "last_name": "Admin",
        "cnic": "4444444444444",
        "role": "system_admin",
    },
]


def seed():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env")
        sys.exit(1)
    hashed = hash_password(ADMIN_PASSWORD)
    engine = create_engine(database_url)
    now = datetime.now(timezone.utc).isoformat()
    with engine.begin() as conn:
        for admin in HARDCODED_ADMINS:
            r = conn.execute(
                text(
                    "SELECT id FROM public.users WHERE email = :email"
                ),
                {"email": admin["email"]},
            ).fetchone()
            if r:
                conn.execute(
                    text("""
                        UPDATE public.users
                        SET hashed_password = :pw, role = :role,
                            first_name = :fn, last_name = :ln, cnic = :cnic
                        WHERE email = :email
                    """),
                    {
                        "pw": hashed,
                        "role": admin["role"],
                        "fn": admin["first_name"],
                        "ln": admin["last_name"],
                        "cnic": admin["cnic"],
                        "email": admin["email"],
                    },
                )
                logger.info("Updated admin: %s (%s)", admin["email"], admin["role"])
            else:
                conn.execute(
                    text("""
                        INSERT INTO public.users
                        (first_name, last_name, cnic, email, hashed_password, role, created_at)
                        VALUES (:fn, :ln, :cnic, :email, :pw, :role, :created_at)
                    """),
                    {
                        "fn": admin["first_name"],
                        "ln": admin["last_name"],
                        "cnic": admin["cnic"],
                        "email": admin["email"],
                        "pw": hashed,
                        "role": admin["role"],
                        "created_at": now,
                    },
                )
                logger.info("Created admin: %s (%s)", admin["email"], admin["role"])
    print("\nDone. Use these to log in at /admin/auth/login (all password: Admin@123):")
    for a in HARDCODED_ADMINS:
        print("  ", a["email"], " -> role:", a["role"])


if __name__ == "__main__":
    seed()
