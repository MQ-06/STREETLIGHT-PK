from db.database import SessionLocal

# ✅ LOAD ALL MODELS (IMPORTANT)
from model import users
from model import report
from model import verification
from model import report_logs
from model import routing_table
from model import user_profile  

# 👇 actual import
from model.report import Report, ReportStatus

db = SessionLocal()

report = Report(
    user_id=1,
    title="Test pothole",
    description="big pothole",
    category="POTHOLE",
    location_address="Test Street",
    status=ReportStatus.PENDING,
    combined_score=45  
)

db.add(report)
db.commit()

print("✅ Test report inserted:", report.id)

db.close()