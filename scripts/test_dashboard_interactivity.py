import httpx
import json

BASE_URL = "http://localhost:3847"

def test_dashboard():
    with httpx.Client() as client:
        # 1. Post a dummy observation
        print("[*] Posting dummy observation...")
        obs = {
            "id": "test-obs-123",
            "contexto": "Test Connection",
            "propuesta": "Should we automate this test?"
        }
        client.post(f"{BASE_URL}/api/observations", json=obs)
        
        # 2. Check observations
        print("[*] Checking observations...")
        resp = client.get(f"{BASE_URL}/api/observations")
        print(f"Observations: {resp.json()['count']}")
        
        # 3. Post a decision
        print("[*] Posting decision...")
        decision = {
            "id": "test-obs-123",
            "action": "sí",
            "proposal": "Should we automate this test?"
        }
        resp = client.post(f"{BASE_URL}/api/observations/decide", json=decision)
        print(f"Decision response: {resp.json()}")
        
        # 4. Success check
        resp = client.get(f"{BASE_URL}/api/observations")
        print(f"Remaining observations (should be 0): {resp.json()['count']}")

if __name__ == "__main__":
    try:
        test_dashboard()
    except Exception as e:
        print(f"Error: {e}")
