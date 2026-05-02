# script/test_insert.py
from db.database import SessionLocal
from model.report import Report, ReportStatus, IssueCategory, KanbanStage
from datetime import datetime, timezone, timedelta

db = SessionLocal()

# 1. HIGH SCORE → will trigger AUTO_VERIFY
r1 = Report(
    user_id=1, title="Big Pothole on Main Blvd",
    description="Deep pothole causing accidents",
    category=IssueCategory.POTHOLE,
    location_address="Main Blvd, Lahore",
    status=ReportStatus.PENDING,
    combined_score=90.0,   # ≥ 85 → AUTO_VERIFY
    community_score=0,
)

# 2. LOW SCORE → will trigger REJECT
r2 = Report(
    user_id=1, title="Blurry trash photo",
    description="Unclear image submitted",
    category=IssueCategory.TRASH,
    location_address="Gulberg, Lahore",
    status=ReportStatus.PENDING,
    combined_score=30.0,   # < 60 → REJECT
    community_score=0,
)

# 3. MID SCORE → will trigger MOVE_REVIEW
r3 = Report(
    user_id=1, title="Possible garbage dump",
    description="Not sure if this qualifies",
    category=IssueCategory.TRASH,
    location_address="DHA, Lahore",
    status=ReportStatus.PENDING,
    combined_score=70.0,   # 60-85 → MOVE_REVIEW
    community_score=0,
)

# 4. COMMUNITY VOTES → will trigger VERIFY_AND_ASSIGN
r4 = Report(
    user_id=1, title="Confirmed pothole by community",
    description="Multiple users confirmed",
    category=IssueCategory.POTHOLE,
    location_address="Johar Town, Lahore",
    status=ReportStatus.PENDING,
    combined_score=65.0,
    community_score=5,     # ≥ 3 → VERIFY_AND_ASSIGN
)

# 5. STALLED IN_PROGRESS → will trigger NEEDS_LLM (ask_llm fires here!)
r5 = Report(
    user_id=1, title="Old stalled complaint",
    description="Been in progress for days",
    category=IssueCategory.POTHOLE,
    location_address="Model Town, Lahore",
    status=ReportStatus.IN_PROGRESS,
    combined_score=72.0,
    community_score=0,
    updated_at=datetime.now(timezone.utc) - timedelta(hours=50),  # stalled > 48hrs
)

for r in [r1, r2, r3, r4, r5]:
    db.add(r)

db.commit()
print("✅ All 5 demo reports inserted")
db.close()