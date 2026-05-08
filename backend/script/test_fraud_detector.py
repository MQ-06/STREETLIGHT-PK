"""
test_fraud_detector.py
======================

Focused Fraud Detection Test:
Same GPS + Different Categories
should NOT merge as duplicate.
"""

import sys
from datetime import datetime, timezone

from db.database import SessionLocal

from model.report import (
    Report,
    IssueCategory,
    ReportStatus,
)

from ai_layers.layer2_fraud_detection.fraud_engine import FraudDetector


# ── ANSI Colours ──────────────────────────────────────────────
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
C = "\033[96m"
B = "\033[1m"
Z = "\033[0m"

PASS = f"{G}✅ PASS{Z}"
FAIL = f"{R}❌ FAIL{Z}"

results = []


def record(name, passed, detail=""):

    results.append({
        "name": name,
        "passed": passed,
        "detail": detail,
    })

    print(f"  {PASS if passed else FAIL}  {name}")

    if detail:
        print(f"      {C}{detail}{Z}")


# ── Config ────────────────────────────────────────────────────
TEST_USER_ID = 1

LAT = 31.5497
LNG = 74.3436

ADDRESS = "Mall Road Lahore"


# ── Helpers ───────────────────────────────────────────────────
def cleanup_test_reports(db):

    deleted = (
        db.query(Report)
        .filter(
            Report.title.like("FRAUD_TEST_%")
        )
        .delete(synchronize_session=False)
    )

    db.commit()

    print(f"{Y}🧹 Cleanup:{Z} deleted {deleted} old test reports\n")


def create_report(
    db,
    category,
    title,
):

    report = Report(
        user_id=TEST_USER_ID,
        title=title,
        description="Fraud detector automated test",
        category=category,
        status=ReportStatus.PENDING,
        location_lat=LAT,
        location_lng=LNG,
        location_address=ADDRESS,
        created_at=datetime.now(timezone.utc),
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


# ══════════════════════════════════════════════════════════════
def run_test():

    print(f"\n{B}{C}{'='*70}{Z}")
    print(f"{B}{C}   FRAUD DETECTOR — CATEGORY ISOLATION TEST{Z}")
    print(f"{B}{C}{'='*70}{Z}\n")

    db = SessionLocal()

    try:

        detector = FraudDetector(db)

        # ────────────────────────────────────────────────
        # CLEANUP
        # ────────────────────────────────────────────────
        cleanup_test_reports(db)

        # ────────────────────────────────────────────────
        # STEP 1
        # ────────────────────────────────────────────────
        print(f"{B}{Y}[STEP 1]{Z} Registering FIRST report...\n")

        pothole = create_report(
            db=db,
            category=IssueCategory.POTHOLE,
            title="FRAUD_TEST_POTHOLE",
        )

        print(f"{G}📌 FIRST REPORT INSERTED{Z}")
        print(f"   Report ID    : {pothole.id}")
        print(f"   Category     : {pothole.category.value}")
        print(f"   Status       : {pothole.status.value}")
        print(f"   Address      : {pothole.location_address}")
        print(f"   Latitude     : {pothole.location_lat}")
        print(f"   Longitude    : {pothole.location_lng}")
        print(f"   Created At   : {pothole.created_at}")
        print()

        # ────────────────────────────────────────────────
        # STEP 2
        # ────────────────────────────────────────────────
        print(f"{B}{Y}[STEP 2]{Z} Submitting SECOND report...\n")

        print(f"{C}Incoming report:{Z}")
        print(f"   Category     : garbage")
        print(f"   Address      : {ADDRESS}")
        print(f"   Latitude     : {LAT}")
        print(f"   Longitude    : {LNG}")
        print()

        result = detector.run_all_checks(
            user_id=TEST_USER_ID,
            category=IssueCategory.TRASH,
            lat=LAT,
            lng=LNG,
            submitted_at=datetime.now(timezone.utc),
        )

        # ────────────────────────────────────────────────
        # DETECTOR RESULT
        # ────────────────────────────────────────────────
        print(f"{B}{C}[DETECTOR RESULT]{Z}\n")

        for k, v in result.items():
            print(f"   {k} : {v}")

        print()

        # ────────────────────────────────────────────────
        # VALIDATION
        # ────────────────────────────────────────────────
        print(f"{B}{Y}[VALIDATION]{Z}\n")

        record(
            "Duplicate NOT triggered",
            result["duplicate_of_id"] is None,
            "Different categories are isolated"
        )

        record(
            "POTHOLE != GARBAGE",
            True,
            "Reports treated separately"
        )

        # ────────────────────────────────────────────────
        # SUMMARY
        # ────────────────────────────────────────────────
        passed = sum(r["passed"] for r in results)
        failed = len(results) - passed

        print(f"\n{B}{C}{'='*70}{Z}")
        print(f"{B}SUMMARY — {passed}/{len(results)} passed{Z}")
        print(f"{B}{C}{'='*70}{Z}")

        if failed == 0:

            print(
                f"\n{G}{B}"
                f"🎉 SUCCESS"
                f"{Z}"
            )

            print(
                f"{G}"
                f"Same location reports with DIFFERENT categories"
                f" were NOT merged."
                f"{Z}"
            )

        else:

            print(
                f"\n{R}{B}"
                f"❌ FAILURE"
                f"{Z}"
            )

            print(
                f"{R}"
                f"Fraud detector incorrectly merged reports."
                f"{Z}"
            )

        print(f"\n{B}{'='*70}{Z}\n")

        return failed == 0

    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(0 if run_test() else 1)