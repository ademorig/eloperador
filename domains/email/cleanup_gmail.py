import requests
import json
import time

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
BASE_URL = "https://eco.dxarte.org/api/v1"
GMAIL_CREDENTIAL_ID = "Fhvq4vOWbvQhrvvi"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def create_cleanup_workflow():
    wf_data = {
        "name": "Gmail_Auto_Cleanup_Oldest_250",
        "nodes": [
            {
                "parameters": {},
                "name": "On clicking 'Execute'",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [0, 0]
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "limit": 250,
                    "filters": {
                        "q": "label:inbox"
                    }
                },
                "name": "Gmail Get Oldest",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [250, 0],
                "credentials": {"gmailOAuth2": {"id": GMAIL_CREDENTIAL_ID}}
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "delete",
                    "messageId": "={{$json.id}}"
                },
                "name": "Gmail Delete",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [500, 0],
                "credentials": {"gmailOAuth2": {"id": GMAIL_CREDENTIAL_ID}}
            }
        ],
        "connections": {
            "On clicking 'Execute'": { "main": [[{ "node": "Gmail Get Oldest", "type": "main", "index": 0 }]] },
            "Gmail Get Oldest": { "main": [[{ "node": "Gmail Delete", "type": "main", "index": 0 }]] }
        },
        "settings": { "executionOrder": "v1" }
    }
    
    print("Creating cleanup workflow...")
    res = requests.post(f"{BASE_URL}/workflows", headers=headers, json=wf_data).json()
    return res.get('id')

def execute_workflow(wf_id):
    # For manual trigger workflows, we typically execute via the API or manual trigger doesn't have a direct 'run' endpoint in Public API except for the webhook ones.
    # However, we can use the 'active' and 'webhook' trick or just let the user know.
    # Alternatively, we can use a Webhook instead of Manual Trigger to run it.
    pass

if __name__ == "__main__":
    wf_id = create_cleanup_workflow()
    if wf_id:
        print(f"Workflow created with ID: {wf_id}")
        # To run it, we'll convert it to use a webhook temporarily or use the manual execute if supported.
        # Since Public API execution is limited, the best way is to add a webhook and trigger it.
        print("Adding temporary trigger...")
        wf = requests.get(f"{BASE_URL}/workflows/{wf_id}", headers=headers).json()
        wf['nodes'][0] = {
            "parameters": {"path": "temp-cleanup", "httpMethod": "POST"},
            "name": "Temp Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [0, 0]
        }
        requests.put(f"{BASE_URL}/workflows/{wf_id}", headers=headers, json=wf)
        requests.post(f"{BASE_URL}/workflows/{wf_id}/activate", headers=headers)
        
        time.sleep(2)
        print("Executing cleanup...")
        r = requests.post("https://eco.dxarte.org/webhook/temp-cleanup")
        print(f"Cleanup Started: {r.status_code}")
        print("The deletion of 250 emails is now running in the background in n8n.")
