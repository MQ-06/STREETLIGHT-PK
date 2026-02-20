from db.database import engine, Base
from model.users import User
from model.user_profile import UserProfile 
from model.report import Report, ReportInteraction


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__=="__main__":
    create_tables()