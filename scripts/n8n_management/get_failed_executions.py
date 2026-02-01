import requests
import os
import json

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    url = "https://eco.dxarte.org/api/v1/executions?limit=5"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            executions = response.json().get('data', [])
            for ex in executions:
                print(f"ID: {ex.get('id')}, Status: {ex.get('status')}, Workflow: {ex.get('workflowId')}")
                # If failed, look for more details
                if ex.get('status') == 'failed':
                    details = requests.get(f"https://eco.dxarte.org/api/v1/executions/{ex.get('id')}", headers=headers).json()
                    print(f"  Error: {details.get('error')}")
        else:
            print(f"Error fetching executions: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
