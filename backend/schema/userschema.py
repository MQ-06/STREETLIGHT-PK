from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    cnic: str
    email: EmailStr
    password: str

# Login request
class UserLogin(BaseModel):
    email: str
    password: str

# Forget Password request
class ForgetPasswordRequest(BaseModel):
    email: str

# Reset Password request
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class SignupResponse(BaseModel):
    message: str
    user_id: int

