"""
Seed script — adds realistic Faisalabad test reports so the
Super Admin dashboard shows multiple city cards.

Run from backend/:
    python -m script.seed_faisalabad
"""
import sys, random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, '.')
from db.database import SessionLocal
from model.report import Report, IssueCategory, KanbanStage, ReportStatus
from model.routing_table import RoutingTable

# ── Config ────────────────────────────────────────────────────────────────────
REPORTER_IDS   = [1, 2, 3, 4, 5, 6, 7, 8]   # existing citizen IDs
DAYS_BACK      = 30                            # spread over last 30 days

# Faisalabad GPS samples (within bounds 31.30-31.52 lat, 72.95-73.20 lng)
FAISALABAD_COORDS = [
    (31.4187, 73.0790),  # Clock Tower area
    (31.4500, 73.1350),  # Peoples Colony
    (31.4020, 73.0650),  # Millat Town
    (31.4800, 73.0900),  # Madina Town
    (31.4300, 73.1100),  # D-Ground
    (31.4650, 73.0500),  # Jinnah Colony
    (31.3850, 73.0400),  # Gulistan Colony
    (31.5050, 73.1500),  # Khurianwala
]

# Realistic seeding spec — mirrors the module spec sample data:
#   HIGH RISK zone: 234 reports, 44% re-report, 11.2d avg, forecast +58
#   MED RISK zone:  142 reports, 18% re-report, 5.9d avg, forecast +18
# We seed ~40 reports to keep DB light but show variety.

SEEDS = [
    # (category, stage, avg_res_days, community_score, is_dup)
    # -- HIGH volume, slow resolution, many dups (simulates a troubled area)
    *[(IssueCategory.TRASH,   KanbanStage.IN_PROGRESS,       11.0, 54.0, False)] * 8,
    *[(IssueCategory.POTHOLE, KanbanStage.PENDING_VERIFICATION, 0.5, None, False)] * 5,
    *[(IssueCategory.TRASH,   KanbanStage.NEW,                 0.0, None, True)]  * 6,  # dups
    *[(IssueCategory.POTHOLE, KanbanStage.RESOLVED,            9.5, 55.0, False)] * 5,
    *[(IssueCategory.TRASH,   KanbanStage.AWAITING_FEEDBACK,   6.0, 60.0, False)] * 4,
    *[(IssueCategory.POTHOLE, KanbanStage.VERIFIED,            2.0, None, False)] * 4,
    *[(IssueCategory.TRASH,   KanbanStage.RESOLVED,           12.0, 50.0, False)] * 4,
    *[(IssueCategory.POTHOLE, KanbanStage.IN_PROGRESS,         8.0, None, True)]  * 4,  # dups
]

random.seed(42)

def _ago(days_float):
    return datetime.now(timezone.utc) - timedelta(days=days_float)


def run():
    db = SessionLocal()

    # Look up Faisalabad officer IDs from routing table
    fmc_row  = db.query(RoutingTable).filter_by(city='faisalabad', department='fmc',  is_active=True).first()
    fwmc_row = db.query(RoutingTable).filter_by(city='faisalabad', department='fwmc', is_active=True).first()

    if not fmc_row or not fwmc_row:
        print('ERROR: Faisalabad routing rows not found. Run the routing seed first.')
        db.close()
        return

    dept_map = {
        IssueCategory.POTHOLE: ('fmc',  fmc_row.officer_id),
        IssueCategory.TRASH:   ('fwmc', fwmc_row.officer_id),
    }

    created = []
    for i, (cat, stage, res_days, comm_score, is_dup) in enumerate(SEEDS):
        dept_slug, officer_id = dept_map[cat]

        # Spread created_at over last DAYS_BACK days
        created_offset = random.uniform(0, DAYS_BACK)
        created_at     = _ago(created_offset)

        # updated_at simulates time spent in current stage
        if stage == KanbanStage.RESOLVED:
            updated_at = created_at + timedelta(days=res_days)
        else:
            updated_at = created_at + timedelta(days=random.uniform(0, res_days or 1))

        lat, lng = random.choice(FAISALABAD_COORDS)
        # Tiny jitter so coords aren't all identical
        lat += random.uniform(-0.005, 0.005)
        lng += random.uniform(-0.005, 0.005)

        rep = Report(
            user_id             = random.choice(REPORTER_IDS),
            title               = '%s issue in Faisalabad' % cat.value.title(),
            description         = 'Seeded test report #%d for analytics dashboard.' % (i + 1),
            category            = cat,
            location_address    = 'Faisalabad, Punjab',
            location_city       = 'Faisalabad',
            location_lat        = round(lat, 6),
            location_lng        = round(lng, 6),
            status              = ReportStatus.VERIFIED,
            assigned_city       = 'faisalabad',
            assigned_department = dept_slug,
            assigned_officer_id = officer_id,
            kanban_stage        = stage,
            community_score     = comm_score,
            ai_confidence       = round(random.uniform(70, 95), 1),
            validation_status   = 'passed',
            gps_verified        = True,
            created_at          = created_at,
            updated_at          = updated_at,
        )
        db.add(rep)
        db.flush()   # get rep.id before setting duplicate_of_id

        if is_dup and created:
            rep.duplicate_of_id = random.choice(created).id

        created.append(rep)

    db.commit()
    print('Seeded %d Faisalabad reports.' % len(SEEDS))

    # Quick summary
    from collections import Counter
    all_reports = db.query(Report.assigned_city).all()
    counts = Counter(r.assigned_city for r in all_reports)
    print('DB city totals:')
    for city, n in counts.most_common():
        print('  %s: %d reports' % (repr(city), n))

    db.close()


if __name__ == '__main__':
    run()
