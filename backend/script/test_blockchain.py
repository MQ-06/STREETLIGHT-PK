# # script/test_blockchain.py
# import sys
# import os
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # Sare models import karo — SQLAlchemy ko sab chahiye
# from model.users import User
# from model.user_profile import UserProfile   # ← YE ADD KARO
# from model.report import ReportStatus
# from model.verification import VerificationStatus  # ← YE BHI (agar hai)
# from db.database import SessionLocal
# from ai_layers.layer5_final_score.score_calculator import FinalScoreCalculator

# db = SessionLocal()
# calculator = FinalScoreCalculator(db)
# result = calculator.calculate_final_score(report_id=1)
# print(result)
# script/test_blockchain.py — replace with this
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# YE PEHLE — .env load karo
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env'))

# Verify ho raha hai?
print("ENABLED:", os.getenv("BLOCKCHAIN_ENABLED"))
print("RPC:", os.getenv("BLOCKCHAIN_RPC_URL"))
print("CONTRACT:", os.getenv("CONTRACT_ADDRESS"))
print("KEY:", os.getenv("DEPLOYER_PRIVATE_KEY", "")[:10] + "...")

# PHIR import karo
from blockchain.blockchain_service import blockchain_service

result = blockchain_service.register_complaint(
    complaint_id        = 999,
    image_url           = "https://test.cloudinary.com/test.jpg",
    category            = "GARBAGE",
    latitude            = 31.5204,
    longitude           = 74.3587,
    verification_status = "AUTO_VERIFIED",
    ai_score            = 92.0,
    final_score         = 87.5,
)
print("Result:", result)

proof = blockchain_service.get_complaint_proof(999)
print("Proof:", proof)