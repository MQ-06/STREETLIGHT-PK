#script/test_blockchain.py
from db.database import SessionLocal
from ai_layers.layer5_final_score.score_calculator import FinalScoreCalculator

db = SessionLocal()

calculator = FinalScoreCalculator(db)

result = calculator.calculate_final_score(report_id=1)

print(result)