import requests
import os
from dotenv import load_dotenv

def check_status():
    # Use the token from verify_activation.py which seemed to work (200 OK)
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI'
    url = 'https://eco.dxarte.org/api/v1/workflows'
    headers = {'X-N8N-API-KEY': token}
    
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            data = r.json().get('data', [])
            print(f"Total Workflows: {len(data)}")
            for w in data:
                name = w.get("name").encode("ascii", "ignore").decode()
                active = w.get("active")
                print(f"- {name} (Active: {active})")
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_status()
