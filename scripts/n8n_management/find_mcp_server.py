import requests
import os
from pathlib import Path

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    url = "https://eco.dxarte.org/api/v1/workflows"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            workflows = response.json().get('data', [])
            for wf_summary in workflows:
                wf_id = wf_summary.get('id')
                wf_details = requests.get(f"{url}/{wf_id}", headers=headers).json()
                nodes = wf_details.get('nodes', [])
                for node in nodes:
                    if node.get('type') == 'n8n-nodes-base.webhook':
                        path = node.get('parameters', {}).get('path')
                        if path and 'mcp' in path:
                            print(f"Workflow: {wf_summary.get('name')} (ID: {wf_id})")
                            print(f"  Webhook Path: {path}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
