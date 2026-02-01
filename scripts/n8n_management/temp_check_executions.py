import requests
import os
from datetime import datetime, timedelta

def check_executions():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI'
    # List executions
    url = 'https://eco.dxarte.org/api/v1/executions'
    headers = {'X-N8N-API-KEY': token}
    
    try:
        # Get executions from the last 24 hours
        params = {
            'limit': 10
        }
        r = requests.get(url, headers=headers, params=params)
        if r.status_code == 200:
            data = r.json().get('data', [])
            print(f"Recent Executions (Last 10):")
            if not data:
                print("No executions found in the recent history.")
            for exe in data:
                wf_id = exe.get('workflowId')
                status = exe.get('status')
                started = exe.get('startedAt')
                mode = exe.get('mode')
                print(f"- WF ID: {wf_id} | Status: {status} | Started: {started} | Mode: {mode}")
        else:
            print(f"Error {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    check_executions()
