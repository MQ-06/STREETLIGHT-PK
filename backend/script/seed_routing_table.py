"""
Seed: Admin accounts + routing table — Phase 1
===============================================
Creates 7 user accounts (roles: super_admin, city_admin, dept_officer)
and inserts 4 routing rows mapping (city, department) → officer.

Password for ALL accounts: Admin@123

Account summary:
  super_admin@streetlight.local          → Super Admin  (sees all Pakistan)
  lahore_ca@streetlight.local            → City Admin, Lahore
  faisalabad_ca@streetlight.local        → City Admin, Faisalabad
  ahmad.raza@streetlight.local           → Dept Officer, Lahore / LMC (potholes)
  sara.khan@streetlight.local            → Dept Officer, Lahore / LWMC (garbage)
  bilal.chaudhry@streetlight.local       → Dept Officer, Faisalabad / FMC (potholes)
  ayesha.nawaz@streetlight.local         → Dept Officer, Faisalabad / FWMC (garbage)

Routing table (4 rows):
  lahore     + lmc  → Ahmad Raza
  lahore     + lwmc → Sara Khan
  faisalabad + fmc  → Bilal Chaudhry
  faisalabad + fwmc → Ayesha Nawaz

Safe to re-run (idempotent — upserts on email).

Usage:
    cd backend
    python script/seed_routing_table.py
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

ADMIN_PASSWORD = "Admin@123"

# ── 7 admin accounts ─────────────────────────────────────────────────────────
ADMIN_ACCOUNTS = [
    {
        "email":      "super_admin@streetlight.local",
        "first_name": "Super",
        "last_name":  "Admin",
        "cnic":       "3520100000001",
        "role":       "super_admin",
    },
    {
        "email":      "lahore_ca@streetlight.local",
        "first_name": "Lahore",
        "last_name":  "CityAdmin",
        "cnic":       "3520100000002",
        "role":       "city_admin",
        "city":       "lahore",
    },
    {
        "email":      "faisalabad_ca@streetlight.local",
        "first_name": "Faisalabad",
        "last_name":  "CityAdmin",
        "cnic":       "3310100000003",
        "role":       "city_admin",
        "city":       "faisalabad",
    },
    {
        "email":              "ahmad.raza@streetlight.local",
        "first_name":         "Ahmad",
        "last_name":          "Raza",
        "cnic":               "3520100000004",
        "role":               "dept_officer",
        "city":               "lahore",
        "notification_email": "bitf22m006@pucit.edu.pk",
    },
    {
        "email":              "sara.khan@streetlight.local",
        "first_name":         "Sara",
        "last_name":          "Khan",
        "cnic":               "3520100000005",
        "role":               "dept_officer",
        "city":               "lahore",
        "notification_email": "bitf22m044@pucit.edu.pk",
    },
    {
        "email":              "bilal.chaudhry@streetlight.local",
        "first_name":         "Bilal",
        "last_name":          "Chaudhry",
        "cnic":               "3310100000006",
        "role":               "dept_officer",
        "city":               "faisalabad",
        "notification_email": "bitf22m011@pucit.edu.pk",
    },
    {
        "email":              "ayesha.nawaz@streetlight.local",
        "first_name":         "Ayesha",
        "last_name":          "Nawaz",
        "cnic":               "3310100000007",
        "role":               "dept_officer",
        "city":               "faisalabad",
        "notification_email": "bitf22m015@pucit.edu.pk",
    },
]

# ── 4 routing rows (officer looked up by email after accounts are seeded) ────
ROUTING_ROWS = [
    {
        "city":             "lahore",
        "department":       "lmc",
        "department_name":  "Lahore Metropolitan Corporation",
        "officer_email":    "ahmad.raza@streetlight.local",
    },
    {
        "city":             "lahore",
        "department":       "lwmc",
        "department_name":  "Lahore Waste Management Company",
        "officer_email":    "sara.khan@streetlight.local",
    },
    {
        "city":             "faisalabad",
        "department":       "fmc",
        "department_name":  "Faisalabad Metropolitan Corporation",
        "officer_email":    "bilal.chaudhry@streetlight.local",
    },
    {
        "city":             "faisalabad",
        "department":       "fwmc",
        "department_name":  "Faisalabad Waste Management Company",
        "officer_email":    "ayesha.nawaz@streetlight.local",
    },
]


def seed() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL not set in .env")
        sys.exit(1)

    hashed_pw = hash_password(ADMIN_PASSWORD)
    engine    = create_engine(database_url)
    now       = datetime.now(timezone.utc).isoformat()

    with engine.begin() as conn:

        # ── 1. Upsert admin user accounts ─────────────────────────────────
        logger.info("── Seeding admin accounts ──────────────────────────────")
        for acc in ADMIN_ACCOUNTS:
            existing = conn.execute(
                text("SELECT id FROM public.users WHERE email = :email"),
                {"email": acc["email"]},
            ).fetchone()

            if existing:
                conn.execute(
                    text("""
                        UPDATE public.users
                        SET first_name         = :fn,
                            last_name          = :ln,
                            cnic               = :cnic,
                            hashed_password    = :pw,
                            role               = :role,
                            city               = :city,
                            notification_email = :notif_email
                        WHERE email = :email
                    """),
                    {
                        "fn":          acc["first_name"],
                        "ln":          acc["last_name"],
                        "cnic":        acc["cnic"],
                        "pw":          hashed_pw,
                        "role":        acc["role"],
                        "city":        acc.get("city"),
                        "notif_email": acc.get("notification_email"),
                        "email":       acc["email"],
                    },
                )
                logger.info(f"  updated  {acc['email']}  ({acc['role']})")
            else:
                conn.execute(
                    text("""
                        INSERT INTO public.users
                            (first_name, last_name, cnic, email, hashed_password, role, city, notification_email, created_at)
                        VALUES
                            (:fn, :ln, :cnic, :email, :pw, :role, :city, :notif_email, :created_at)
                    """),
                    {
                        "fn":          acc["first_name"],
                        "ln":          acc["last_name"],
                        "cnic":        acc["cnic"],
                        "email":       acc["email"],
                        "pw":          hashed_pw,
                        "role":        acc["role"],
                        "city":        acc.get("city"),
                        "notif_email": acc.get("notification_email"),
                        "created_at":  now,
                    },
                )
                logger.info(f"  created  {acc['email']}  ({acc['role']})")

        # ── 2. Upsert routing rows ─────────────────────────────────────────
        logger.info("── Seeding routing table ───────────────────────────────")
        for row in ROUTING_ROWS:
            officer = conn.execute(
                text("SELECT id, first_name, last_name FROM public.users WHERE email = :email"),
                {"email": row["officer_email"]},
            ).fetchone()

            if not officer:
                logger.error(
                    f"  SKIP: officer not found for email={row['officer_email']}. "
                    "Run this script again after fixing the accounts."
                )
                continue

            officer_id   = officer[0]
            officer_name = f"{officer[1]} {officer[2]}"

            existing_row = conn.execute(
                text("""
                    SELECT id FROM public.routing_table
                    WHERE city = :city AND department = :dept
                """),
                {"city": row["city"], "dept": row["department"]},
            ).fetchone()

            if existing_row:
                conn.execute(
                    text("""
                        UPDATE public.routing_table
                        SET officer_id      = :officer_id,
                            department_name = :dept_name,
                            is_active       = TRUE
                        WHERE city = :city AND department = :dept
                    """),
                    {
                        "officer_id": officer_id,
                        "dept_name":  row["department_name"],
                        "city":       row["city"],
                        "dept":       row["department"],
                    },
                )
                logger.info(
                    f"  updated  {row['city']:12s} + {row['department']:5s} → {officer_name}"
                )
            else:
                conn.execute(
                    text("""
                        INSERT INTO public.routing_table
                            (city, department, department_name, officer_id, is_active, created_at)
                        VALUES
                            (:city, :dept, :dept_name, :officer_id, TRUE, :created_at)
                    """),
                    {
                        "city":       row["city"],
                        "dept":       row["department"],
                        "dept_name":  row["department_name"],
                        "officer_id": officer_id,
                        "created_at": now,
                    },
                )
                logger.info(
                    f"  created  {row['city']:12s} + {row['department']:5s} → {officer_name}"
                )

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("Seeding complete. Login credentials (all: Admin@123)")
    print("=" * 60)
    for acc in ADMIN_ACCOUNTS:
        print(f"  {acc['email']:<45}  role: {acc['role']}")
    print()
    print("Routing table:")
    for row in ROUTING_ROWS:
        print(f"  {row['city']:12s} + {row['department']:5s} → {row['officer_email']}")
    print("=" * 60)


if __name__ == "__main__":
    seed()
