
import requests

try:
    res = requests.post("http://127.0.0.1:8000/auth/register", json={
        "name": "Test User",
        "email": "test_debug@example.com",
        "password": "password123"
    })
    print(f"Status Code: {res.status_code}")
    print(f"Response Text: {res.text}")
except Exception as e:
    print(f"Request failed: {e}")
