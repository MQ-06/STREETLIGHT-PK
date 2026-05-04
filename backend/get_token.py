import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_token():
    # Try login first
    login_data = {
        "email": "tester@example.com",
        "password": "Password@123"
    }
    
    response = requests.post(f"{BASE_URL}/login", json=login_data)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    
    # If login fails, try signup
    signup_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "tester@example.com",
        "password": "Password@123",
        "cnic": "12345-6789012-3",
        "phone": "0300-1234567",
        "location": "Lahore"
    }
    
    response = requests.post(f"{BASE_URL}/signup", json=signup_data)
    
    if response.status_code == 201 or response.status_code == 200:
        # Retry login
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
            
    print(f"Error: {response.status_code} - {response.text}")
    return None

if __name__ == "__main__":
    token = get_token()
    if token:
        print(token)
