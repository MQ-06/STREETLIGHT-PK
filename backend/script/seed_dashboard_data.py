"""
Comprehensive seed script for all analytics dashboards.

Creates realistic data for:
  - Lahore    → 60 reports spread across all stages, both depts, proper timestamps
  - Faisalabad → patches existing resolved reports with realistic timestamps

Run from backend/:
    python -m script.seed_dashboard_data
"""
import sys, random
from datetime import datetime, timedelta, timezone
from collections import Counter

sys.path.insert(0, '.')
from db.database import SessionLocal
from model.report import Report, IssueCategory, KanbanStage, ReportStatus

random.seed(99)

NOW      = datetime.now(timezone.utc)
DAYS     = 30
REPORTER_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

# ── Routing constants ─────────────────────────────────────────────────────────
LAHORE_LMC  = dict(city='lahore', dept='lmc',  officer_id=24, cat=IssueCategory.POTHOLE)
LAHORE_LWMC = dict(city='lahore', dept='lwmc', officer_id=25, cat=IssueCategory.TRASH)
FAISA_FMC   = dict(city='faisalabad', dept='fmc',  officer_id=26, cat=IssueCategory.POTHOLE)
FAISA_FWMC  = dict(city='faisalabad', dept='fwmc', officer_id=27, cat=IssueCategory.TRASH)

# ── GPS coords ────────────────────────────────────────────────────────────────
LAHORE_COORDS = [
    (31.5332, 74.2855), (31.6100, 74.2418), (31.6321, 74.2759),
    (31.5500, 74.3200), (31.5800, 74.3500), (31.5200, 74.2600),
    (31.4900, 74.3100), (31.6000, 74.2900), (31.5700, 74.3300),
]
FAISA_COORDS = [
    (31.4187, 73.0790), (31.4500, 73.1350), (31.4020, 73.0650),
    (31.4800, 73.0900), (31.4300, 73.1100), (31.4650, 73.0500),
]

def jitter(lat, lng, r=0.008):
    return round(lat + random.uniform(-r, r), 6), round(lng + random.uniform(-r, r), 6)

def ago(days_f):
    return NOW - timedelta(days=days_f)

# ── Stage definitions: (stage, avg_res_days, community_score_range, is_dup_chance) ──
LAHORE_SEEDS = [
    # Stage                          res_days  comm_score       dup%  count
    (KanbanStage.RESOLVED,           5.0,      (72, 90),        0.0,  12),
    (KanbanStage.RESOLVED,           3.5,      (80, 95),        0.0,   8),
    (KanbanStage.IN_PROGRESS,        0.0,      None,            0.10,  10),
    (KanbanStage.AWAITING_FEEDBACK,  0.0,      (60, 80),        0.05,   7),
    (KanbanStage.PENDING_VERIFICATION, 0.0,    None,            0.15,   9),
    (KanbanStage.VERIFIED,           0.0,      None,            0.05,   6),
    (KanbanStage.NEW,                0.0,      None,            0.20,   8),
]

# For Faisalabad — just fix resolved timestamps so avg_res_days shows correctly
# Existing seeded Faisalabad resolved reports have wrong updated_at

def make_report(routing, stage, created_offset, res_days, comm_range, db):
    lat, lng = jitter(*random.choice(
        LAHORE_COORDS if routing['city'] == 'lahore' else FAISA_COORDS
    ))
    created_at = ago(created_offset)

    if stage == KanbanStage.RESOLVED:
        updated_at = created_at + timedelta(days=res_days + random.uniform(-0.5, 0.5))
    else:
        # Time stuck in current stage: 0.5–4 days
        updated_at = created_at + timedelta(days=random.uniform(0.5, 4.0))

    cat = routing['cat']
    return Report(
        user_id             = random.choice(REPORTER_IDS),
        title               = f"{'Pothole' if cat == IssueCategory.POTHOLE else 'Garbage'} issue reported",
        description         = f"Seeded report for {routing['city']} {routing['dept']} analytics demo.",
        category            = cat,
        location_address    = f"{routing['city'].title()}, Punjab",
        location_city       = routing['city'].title(),
        location_lat        = lat,
        location_lng        = lng,
        status              = ReportStatus.VERIFIED,
        assigned_city       = routing['city'],
        assigned_department = routing['dept'],
        assigned_officer_id = routing['officer_id'],
        kanban_stage        = stage,
        community_score     = round(random.uniform(*comm_range), 1) if comm_range else None,
        ai_confidence       = round(random.uniform(72, 96), 1),
        validation_status   = 'passed',
        gps_verified        = True,
        created_at          = created_at,
        updated_at          = updated_at,
    )


def seed_lahore(db):
    print('\n--- Seeding Lahore ---')
    created_reports = []

    for stage, res_days, comm_range, dup_chance, count in LAHORE_SEEDS:
        # Split roughly 45% POTHOLE (lmc) / 55% TRASH (lwmc)
        for i in range(count):
            routing = LAHORE_LMC if i % 2 == 0 else LAHORE_LWMC
            created_offset = random.uniform(1, DAYS - 2)
            rep = make_report(routing, stage, created_offset, res_days, comm_range, db)
            db.add(rep)
            db.flush()

            # Mark some as duplicates of earlier reports
            if dup_chance > 0 and created_reports and random.random() < dup_chance:
                rep.duplicate_of_id = random.choice(created_reports).id

            created_reports.append(rep)

    print(f'  Added {len(created_reports)} Lahore reports')
    return created_reports


def fix_faisalabad_resolved(db):
    """Patch existing Faisalabad RESOLVED reports with realistic timestamps."""
    print('\n--- Patching Faisalabad resolved timestamps ---')
    resolved = db.query(Report).filter(
        Report.assigned_city == 'faisalabad',
        Report.kanban_stage  == KanbanStage.RESOLVED,
    ).all()

    for rep in resolved:
        if rep.created_at:
            res_days   = random.uniform(7.0, 14.0)    # high res time → HIGH RISK
            rep.updated_at = _to_utc(rep.created_at) + timedelta(days=res_days)

    print(f'  Patched {len(resolved)} Faisalabad resolved reports')


def _to_utc(dt):
    if dt is None:
        return NOW
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def print_summary(db):
    since   = NOW - timedelta(days=30)
    reports = db.query(Report).filter(Report.created_at >= since).all()
    by_city = {}
    for r in reports:
        city = r.assigned_city or 'unassigned'
        by_city.setdefault(city, []).append(r)

    print('\n=== Final DB Summary (last 30d) ===')
    for city, reps in sorted(by_city.items()):
        stages = Counter(r.kanban_stage.value if r.kanban_stage else 'NEW' for r in reps)
        cats   = Counter(r.category.value if r.category else '?' for r in reps)
        dups   = sum(1 for r in reps if r.duplicate_of_id)
        re_rate = round(dups / len(reps) * 100, 1)
        resolved = [r for r in reps if r.kanban_stage == KanbanStage.RESOLVED]
        avg_res = 0.0
        if resolved:
            times = []
            for r in resolved:
                if r.created_at and r.updated_at:
                    d = (_to_utc(r.updated_at) - _to_utc(r.created_at)).total_seconds() / 86400
                    if 0 < d < 365:
                        times.append(d)
            avg_res = round(sum(times)/len(times), 1) if times else 0.0

        print(f'\n  {city.upper()}: {len(reps)} reports')
        print(f'    stages:   {dict(stages)}')
        print(f'    cats:     {dict(cats)}')
        print(f'    dups:     {dups} ({re_rate}% re-report rate)')
        print(f'    avg res:  {avg_res}d (resolved: {len(resolved)})')


def run():
    db = SessionLocal()

    seed_lahore(db)
    fix_faisalabad_resolved(db)

    db.commit()
    print_summary(db)
    db.close()
    print('\nDone.')


if __name__ == '__main__':
    run()
