# backendMain/main.py
from fastapi import FastAPI
from routers import signup, login, forget_password, reset_password
from routers.flutter import mobile_auth
from middleware.cors import setup_cors

from model.users import User
from model.user_profile import UserProfile
from model.report import Report, ReportInteraction 

app = FastAPI()
setup_cors(app)

app.include_router(signup.router)
app.include_router(login.router)
app.include_router(forget_password.router)
app.include_router(reset_password.router)
app.include_router(mobile_auth.router)   

@app.get("/")
def root():
    return {"message": "StreetLight Backend Running"}