import requests
import os

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjozMiwiZW1haWwiOiJ0ZXN0ZXJAZXhhbXBsZS5jb20iLCJyb2xlIjoiY2l0aXplbiIsImV4cCI6MTc3Nzg5MzM5NH0.CPLRhQc5TV-M5WhAYJ2E7yuPeXtOi9BAyQvx_czadoI"

def submit_report(image_path, lat, lon, title, description, city):
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    files = {
        "image": (os.path.basename(image_path), open(image_path, "rb"), "image/png")
    }
    
    data = {
        "title": title,
        "description": description,
        "location_address": "Main Road",
        "location_city": city,
        "location_lat": lat,
        "location_lng": lon
    }
    
    print(f"Submitting report: {title} at ({lat}, {lon})...")
    response = requests.post(f"{BASE_URL}/reports/create", headers=headers, files=files, data=data)
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    import json
    # Test 3.1: Valid pothole in Lahore
    submit_report(
        r"C:\Users\HP\Documents\fyp\STREETLIGHT-PK\backend\pothole_test.png",
        31.5204,
        74.3587,
        "Deep Pothole on Main Road",
        "This pothole is dangerous for bikers.",
        "Lahore"
    )
