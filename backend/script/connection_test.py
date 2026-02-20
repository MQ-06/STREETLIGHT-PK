from sqlalchemy import text
from db.database import engine

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful!")
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_connection()
