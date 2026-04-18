"""
Seed script — fires all 5 predictive alert triggers.

Trigger plan:
  area_warning     → push national re-report rate above 30%
                     add 25 duplicate reports (pointing to existing originals)
  resource_suggest → pending already > 50; skew recent 15d heavier than prior 15d
                     add 20 reports dated within last 10 days (non-resolved)
  seasonal         → window already widened to 90d in backend (Jul 1 is ~74d away)
  dept_nudge       → add 15 TRASH reports RESOLVED with 13-16d resolution
                     pushes national TRASH avg above 10d threshold
  anomaly          → add 18 reports dated TODAY
                     daily_avg ≈ 5, threshold ≈ 15 — today_count = 18 triggers it

Run from backend/:
    python -m script.seed_alert_triggers
"""
import sys, random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, '.')
from db.database import SessionLocal
from model.report import Report, IssueCategory, KanbanStage, ReportStatus

random.seed(42)
NOW = datetime.now(timezone.utc)

REPORTER_IDS  = [1, 2, 3, 4, 5, 6, 7, 8]
LAHORE_COORDS = [
    (31.5332, 74.2855), (31.6100, 74.2418), (31.5800, 74.3500),
    (31.5500, 74.3200), (31.5200, 74.2600), (31.4900, 74.3100),
]
FAISA_COORDS = [
    (31.4187, 73.0790), (31.4500, 73.1350), (31.4020, 73.0650),
]

def jitter(lat, lng, r=0.006):
    return round(lat + random.uniform(-r, r), 6), round(lng + random.uniform(-r, r), 6)

def ago(days_f):
    return NOW - timedelta(days=days_f)

def make(city, dept, officer_id, cat, stage, created_at, updated_at,
         comm_score=None, dup_of=None):
    coords = random.choice(LAHORE_COORDS if city == 'lahore' else FAISA_COORDS)
    lat, lng = jitter(*coords)
    return Report(
        user_id             = random.choice(REPORTER_IDS),
        title               = f"{'Pothole' if cat == IssueCategory.POTHOLE else 'Garbage'} report",
        description         = "Alert-trigger seed report.",
        category            = cat,
        location_address    = f"{city.title()}, Punjab",
        location_city       = city.title(),
        location_lat        = lat,
        location_lng        = lng,
        status              = ReportStatus.VERIFIED,
        assigned_city       = city,
        assigned_department = dept,
        assigned_officer_id = officer_id,
        kanban_stage        = stage,
        community_score     = comm_score,
        ai_confidence       = round(random.uniform(70, 95), 1),
        validation_status   = 'passed',
        gps_verified        = True,
        duplicate_of_id     = dup_of,
        created_at          = created_at,
        updated_at          = updated_at,
    )


def run():
    db = SessionLocal()

    # Fetch a few existing original report IDs to use as dup targets
    originals = db.query(Report.id).filter(
        Report.duplicate_of_id == None,
        Report.assigned_city.in_(['lahore', 'faisalabad'])
    ).limit(20).all()
    original_ids = [r.id for r in originals]

    added = []

    # ── Trigger 1 + 2 + 5: area_warning + resource_suggest + anomaly ──────────
    # Add 25 reports dated TODAY — all duplicates (pushes re-rate > 30%)
    # Being in last 15d also helps trending_up for resource_suggest
    # Being today fires anomaly (18 today > 3 × ~5 daily_avg)
    print("Seeding: area_warning + anomaly + resource_suggest trending boost...")
    for i in range(25):
        # First 18 are strictly today (anomaly trigger)
        if i < 18:
            created_at = NOW.replace(hour=random.randint(0, NOW.hour or 1),
                                     minute=random.randint(0, 59),
                                     second=random.randint(0, 59),
                                     microsecond=0)
        else:
            # Remaining 7 within last 10 days (trending_up boost)
            created_at = ago(random.uniform(1, 10))

        updated_at = created_at + timedelta(hours=random.randint(1, 6))

        # Alternate city/dept
        if i % 3 == 0:
            city, dept, oid, cat = 'lahore', 'lmc', 24, IssueCategory.POTHOLE
        elif i % 3 == 1:
            city, dept, oid, cat = 'lahore', 'lwmc', 25, IssueCategory.TRASH
        else:
            city, dept, oid, cat = 'faisalabad', 'fwmc', 27, IssueCategory.TRASH

        rep = make(city, dept, oid, cat, KanbanStage.NEW, created_at, updated_at,
                   dup_of=random.choice(original_ids) if original_ids else None)
        db.add(rep)
        db.flush()   # flush one-at-a-time to avoid PostgreSQL enum bulk-cast issue
        added.append(rep)

    # ── Trigger 4: dept_nudge — TRASH avg resolution > 10d ───────────────────
    # Add 15 TRASH reports RESOLVED with 13-16 day resolution time
    # Spread over last 25 days so they're in the 30d window
    print("Seeding: dept_nudge (slow TRASH resolution)...")
    for i in range(15):
        created_at  = ago(random.uniform(15, 28))
        res_days    = random.uniform(13.0, 16.0)
        updated_at  = created_at + timedelta(days=res_days)

        city, dept, oid = 'lahore', 'lwmc', 25   # LWMC handles trash in Lahore
        rep = make(city, dept, oid, IssueCategory.TRASH,
                   KanbanStage.RESOLVED, created_at, updated_at,
                   comm_score=round(random.uniform(55, 70), 1))
        db.add(rep)
        db.flush()
        added.append(rep)

    db.commit()
    print(f"Added {len(added)} seed reports total.")

    # ── Verify triggers ───────────────────────────────────────────────────────
    since     = NOW - timedelta(days=30)
    today_s   = NOW.replace(hour=0, minute=0, second=0, microsecond=0)

    all_reps  = db.query(Report).filter(Report.created_at >= since).all()
    total     = len(all_reps)
    re_count  = sum(1 for r in all_reps if r.duplicate_of_id)
    re_rate   = round(re_count / total * 100, 1) if total else 0
    pending   = sum(1 for r in all_reps if r.kanban_stage != KanbanStage.RESOLVED)
    today_cnt = sum(1 for r in all_reps if r.created_at and
                    (r.created_at.replace(tzinfo=timezone.utc) if r.created_at.tzinfo is None
                     else r.created_at) >= today_s)
    daily_avg = round(total / 30, 1)

    half      = 15
    mid       = NOW - timedelta(days=half)
    recent    = sum(1 for r in all_reps if (r.created_at.replace(tzinfo=timezone.utc)
                    if r.created_at.tzinfo is None else r.created_at) >= mid)
    prior     = total - recent
    trending  = recent > prior * 1.10

    # Category avg resolution
    from collections import defaultdict
    cat_dur = defaultdict(list)
    for r in all_reps:
        if r.kanban_stage == KanbanStage.RESOLVED and r.created_at and r.updated_at:
            ca = r.created_at.replace(tzinfo=timezone.utc) if r.created_at.tzinfo is None else r.created_at
            ua = r.updated_at.replace(tzinfo=timezone.utc) if r.updated_at.tzinfo is None else r.updated_at
            d = (ua - ca).total_seconds() / 86400
            if 0 < d < 365:
                cat_dur[r.category.value if r.category else 'UNKNOWN'].append(d)

    print("\n=== Alert Trigger Check ===")
    print(f"  Total (30d):   {total}")
    print(f"  Daily avg:     {daily_avg}")
    print()
    t1 = re_rate > 30
    print(f"  [{'FIRE' if t1 else 'MISS'}] area_warning     re-rate={re_rate}%  (need >30%)")
    t2 = pending > 50 and trending
    print(f"  [{'FIRE' if t2 else 'MISS'}] resource_suggest pending={pending}>50={pending>50}, trending={trending} (recent={recent} prior={prior})")
    monsoon_days = 74  # Jul 1 is ~74 days away from Apr 18
    t3 = monsoon_days <= 90
    print(f"  [{'FIRE' if t3 else 'MISS'}] seasonal         monsoon in ~{monsoon_days}d (window=90d)")
    nudges = [(cat, round(sum(v)/len(v),1)) for cat, v in cat_dur.items() if sum(v)/len(v) > 10]
    t4 = len(nudges) > 0
    print(f"  [{'FIRE' if t4 else 'MISS'}] dept_nudge       slow cats={nudges}")
    all_avgs = [(cat, round(sum(v)/len(v),1)) for cat, v in cat_dur.items()]
    print(f"             all cat avgs: {all_avgs}")
    t5 = today_cnt >= daily_avg * 3
    print(f"  [{'FIRE' if t5 else 'MISS'}] anomaly          today={today_cnt} >= 3×{daily_avg}={round(daily_avg*3,1)}")

    all_fire = all([t1, t2, t3, t4, t5])
    print(f"\n  {'ALL 5 TRIGGERS FIRE' if all_fire else 'Some triggers missed — check above'}")

    db.close()


if __name__ == '__main__':
    run()
