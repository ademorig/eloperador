import requests
import os
from dotenv import load_dotenv
from pathlib import Path

def main():
    load_dotenv()
    token = os.getenv("N8N_API_KEY")
    
    if not token:
        print("Error: N8N_API_KEY no definido en .env")
        return

    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    # Try to list workflows
    url = "https://eco.dxarte.org/api/v1/workflows"
    
    try:
        print(f"Connecting to {url}...")
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            workflows = data.get('data', [])
            print(f"Found {len(workflows)} workflows.")
            for wf in workflows:
                print(f"- {wf.get('name')} (ID: {wf.get('id')}, Active: {wf.get('active')}, Tags: {wf.get('tags')})")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
