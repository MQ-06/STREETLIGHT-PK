"""
Seed reports for the last 7 days so the dashboard trend chart shows real data.

Adds 3–8 reports per day (randomised) across Lahore and Faisalabad, spread
throughout business hours, across all kanban stages.

Run from backend/:
    python -m script.seed_weekly_trends
"""
import sys, random
from datetime import datetime, timedelta, timezone

sys.path.insert(0, '.')
from db.database import SessionLocal
from model.report import Report, IssueCategory, KanbanStage, ReportStatus

random.seed(7)

NOW = datetime.now(timezone.utc)

CITIES = [
    dict(city='lahore',     dept='lmc',  officer_id=24, cat=IssueCategory.POTHOLE),
    dict(city='lahore',     dept='lwmc', officer_id=25, cat=IssueCategory.TRASH),
    dict(city='faisalabad', dept='fmc',  officer_id=26, cat=IssueCategory.POTHOLE),
    dict(city='faisalabad', dept='fwmc', officer_id=27, cat=IssueCategory.TRASH),
]

LAHORE_COORDS = [
    (31.5332, 74.2855), (31.6100, 74.2418), (31.5800, 74.3500),
    (31.5200, 74.2600), (31.6000, 74.2900), (31.5500, 74.3200),
]
FAISA_COORDS = [
    (31.4187, 73.0790), (31.4500, 73.1350), (31.4300, 73.1100),
    (31.4650, 73.0500), (31.4020, 73.0650),
]

# Reports per day: index 0 = 6 days ago, index 6 = today
DAILY_COUNTS = [4, 6, 3, 8, 5, 7, 4]

REPORTER_IDS = [1, 2, 3, 4, 5, 6, 7, 8]

STAGES = [
    KanbanStage.NEW,
    KanbanStage.PENDING_VERIFICATION,
    KanbanStage.VERIFIED,
    KanbanStage.IN_PROGRESS,
    KanbanStage.RESOLVED,
]


def jitter(lat, lng, r=0.007):
    return round(lat + random.uniform(-r, r), 6), round(lng + random.uniform(-r, r), 6)


def run():
    db = SessionLocal()
    total = 0

    for day_offset, count in enumerate(DAILY_COUNTS):
        day_base = NOW - timedelta(days=6 - day_offset)
        for _ in range(count):
            routing = random.choice(CITIES)
            coords  = LAHORE_COORDS if routing['city'] == 'lahore' else FAISA_COORDS
            lat, lng = jitter(*random.choice(coords))

            created_at = day_base.replace(
                hour        = random.randint(7, 21),
                minute      = random.randint(0, 59),
                second      = random.randint(0, 59),
                microsecond = 0,
            )
            stage = random.choice(STAGES)
            is_resolved = stage == KanbanStage.RESOLVED
            updated_at  = created_at + timedelta(hours=random.randint(1, 48)) if is_resolved else created_at

            report = Report(
                user_id             = random.choice(REPORTER_IDS),
                title               = ('Pothole on road' if routing['cat'] == IssueCategory.POTHOLE else 'Garbage pile near street'),
                description         = f"Weekly trend seed — {routing['city']} {routing['dept']}.",
                category            = routing['cat'],
                location_address    = f"{routing['city'].title()}, Punjab",
                location_city       = routing['city'].title(),
                location_lat        = lat,
                location_lng        = lng,
                status              = ReportStatus.RESOLVED if is_resolved else ReportStatus.VERIFIED,
                assigned_city       = routing['city'],
                assigned_department = routing['dept'],
                assigned_officer_id = routing['officer_id'],
                kanban_stage        = stage,
                ai_confidence       = round(random.uniform(68, 97), 1),
                ai_severity         = random.choice(['small', 'medium', 'large']),
                validation_status   = 'passed',
                gps_verified        = True,
                created_at          = created_at,
                updated_at          = updated_at,
            )
            db.add(report)
            total += 1

    db.commit()

    # Summary
    print(f'\nSeeded {total} reports across the last 7 days:')
    for i, count in enumerate(DAILY_COUNTS):
        day = NOW - timedelta(days=6 - i)
        print(f'  {day.strftime("%a %Y-%m-%d")}: {count} reports')

    db.close()
    print('\nDone. Run the dashboard to see real trend data.')


if __name__ == '__main__':
    run()
