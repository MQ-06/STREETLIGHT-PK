# script/test_blockchain.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Sare models import karo — SQLAlchemy ko sab chahiye
from model.users import User
from model.user_profile import UserProfile   # ← YE ADD KARO
from model.report import ReportStatus
from model.verification import VerificationStatus  # ← YE BHI (agar hai)
from db.database import SessionLocal
from ai_layers.layer5_final_score.score_calculator import FinalScoreCalculator

db = SessionLocal()
calculator = FinalScoreCalculator(db)
result = calculator.calculate_final_score(report_id=1)
print(result)
