
import unittest
import requests
import datetime

BASE_URL = "http://127.0.0.1:8000"

class TestMLWorkflow(unittest.TestCase):
    def setUp(self):
        # Register user
        self.email = f"test_{datetime.datetime.now().timestamp()}@example.com"
        self.password = "password"
        requests.post(f"{BASE_URL}/auth/register", json={"name": "Test User", "email": self.email, "password": self.password})
        
        # Login
        res = requests.post(f"{BASE_URL}/auth/login", json={"email": self.email, "password": self.password})
        self.token = res.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
    def test_workflow(self):
        # 1. Create Wallet
        res = requests.post(f"{BASE_URL}/wallet/", json={"name": "Test Wallet", "balance": 1000}, headers=self.headers)
        self.assertEqual(res.status_code, 200)
        wallet_id = res.json()["id"]
        
        # 2. Add Expenses (Historical Data)
        today = datetime.date.today()
        dates = [today - datetime.timedelta(days=i) for i in range(10, 0, -1)]
        
        for i, date in enumerate(dates):
            requests.post(f"{BASE_URL}/expense/", json={
                "amount": 10 + i, # Increasing trend
                "category": "Food",
                "date": date.isoformat(),
                "wallet_id": wallet_id
            }, headers=self.headers)
            
        # 3. Get Forecast
        res = requests.get(f"{BASE_URL}/report/forecast", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        forecast = res.json()["forecast"]
        
        # Verify predictions exist
        self.assertTrue(len(forecast) > 0)
        # Verify increasing trend (rough check)
        self.assertGreater(forecast[-1]["predicted_amount"], forecast[0]["predicted_amount"])
        
        print("ML Forecast Test Passed!")

if __name__ == "__main__":
    unittest.main()
