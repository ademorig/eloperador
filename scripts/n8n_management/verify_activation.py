import requests
import os
import time

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "KC4Tkg1MqFfhyef7"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    try:
        # Check if it exists
        res = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
        if res.status_code == 200:
            wf = res.json()
            print(f"Workflow status: Active={wf.get('active')}")
            
            # Try to activate again
            print("Activating...")
            act_res = requests.post(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}/activate", headers=headers)
            print(f"Activation Status: {act_res.status_code}")
            
            time.sleep(5)
            # Try test webhook URL? 
            # Or just use a different path
            print("Checking again...")
            res2 = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
            print(f"Workflow status now: Active={res2.json().get('active')}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
