"""
Seed GPS-tagged reports for the Hotspot Map (M3 demo).

Creates 60 reports spread across 6 Lahore neighbourhoods with:
  - All kanban stages (so we see blue / orange / green / red pins)
  - All severities (small / medium / large)
  - Realistic clustering so the heatmap shows clear hotspots

Run from backend/:
    python -m script.seed_map_pins
"""
import sys, random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, '.')
from db.database import SessionLocal
from model.report import Report, IssueCategory, KanbanStage, ReportStatus

random.seed(42)
NOW = datetime.now(timezone.utc)

# ── Neighbourhood clusters (centre lat/lng, jitter radius) ────────────────────
CLUSTERS = [
    # (name,            lat,      lng,      radius,  weight)
    ('Gulberg',         31.5204,  74.3587,  0.012,   14),  # city centre — dense
    ('DHA',             31.4697,  74.3936,  0.010,   10),
    ('Johar Town',      31.4697,  74.2728,  0.010,   10),
    ('Model Town',      31.4963,  74.3267,  0.008,    8),
    ('Iqbal Town',      31.5049,  74.3169,  0.008,    9),
    ('Cantonment',      31.5497,  74.3944,  0.009,    9),
]

STAGES = [
    KanbanStage.NEW,
    KanbanStage.PENDING_VERIFICATION,
    KanbanStage.VERIFIED,
    KanbanStage.IN_PROGRESS,
    KanbanStage.AWAITING_FEEDBACK,
    KanbanStage.RESOLVED,
]

# Weighted stage distribution: more active, fewer resolved
STAGE_WEIGHTS = [12, 14, 8, 14, 8, 10]   # sums to 66 ≈ 60 usable

SEVERITIES = ['small', 'medium', 'large']

REPORTER_IDS = [1, 2, 3, 4, 5, 6, 7, 8]


def jitter(lat, lng, r):
    return (
        round(lat + random.uniform(-r, r), 6),
        round(lng + random.uniform(-r, r), 6),
    )


def make_report(lat, lng, stage, severity, category, created_offset):
    created_at = NOW - timedelta(days=created_offset)

    if stage == KanbanStage.RESOLVED:
        updated_at = created_at + timedelta(days=random.uniform(1.5, 7.0))
    else:
        updated_at = created_at + timedelta(hours=random.uniform(1, 48))

    return Report(
        user_id             = random.choice(REPORTER_IDS),
        title               = f"{'Pothole' if category == IssueCategory.POTHOLE else 'Garbage'} spotted",
        description         = "Seeded for map pin demo.",
        category            = category,
        location_address    = "Lahore, Punjab",
        location_city       = "Lahore",
        location_lat        = lat,
        location_lng        = lng,
        status              = ReportStatus.VERIFIED,
        assigned_city       = 'lahore',
        assigned_department = 'lmc' if category == IssueCategory.POTHOLE else 'lwmc',
        assigned_officer_id = 24    if category == IssueCategory.POTHOLE else 25,
        kanban_stage        = stage,
        ai_severity         = severity,
        ai_confidence       = round(random.uniform(70, 97), 1),
        validation_status   = 'passed',
        gps_verified        = True,
        created_at          = created_at,
        updated_at          = updated_at,
    )


def run():
    db = SessionLocal()

    total = 0
    for cluster_name, c_lat, c_lng, radius, count in CLUSTERS:
        # Pick stages for this cluster using weighted random
        stages = random.choices(STAGES, weights=STAGE_WEIGHTS, k=count)
        for stage in stages:
            lat, lng = jitter(c_lat, c_lng, radius)
            severity  = random.choices(SEVERITIES, weights=[3, 5, 2])[0]  # medium-heavy
            category  = random.choice([IssueCategory.POTHOLE, IssueCategory.TRASH])
            offset    = random.uniform(0.5, 28)   # within last 28 days
            rep = make_report(lat, lng, stage, severity, category, offset)
            db.add(rep)
            db.flush()
            total += 1

    db.commit()
    print(f"Seeded {total} map-pin reports across 6 Lahore neighbourhoods.")
    db.close()


if __name__ == '__main__':
    run()
