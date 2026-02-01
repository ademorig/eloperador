import requests
import time
import json

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    base_url = "https://eco.dxarte.org/api/v1"
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    # We will create a fresh workflow to ensure it works as expected
    wf_data = {
        "name": "Delete_Oldest_100_Emails_Fixed",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "delete-100-oldest",
                    "options": {}
                },
                "id": "trigger-1",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [0, 0]
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "limit": 500,
                    "filters": {
                        "q": "label:inbox"
                    }
                },
                "id": "gmail-get",
                "name": "Gmail Get Emails",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [200, 0],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            },
            {
                "parameters": {
                    "jsCode": "// Reverse the order to put oldest first and take 100\nconst items = $input.all();\nreturn items.reverse().slice(0, 100);"
                },
                "id": "sort-node",
                "name": "Pick Oldest 100",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1,
                "position": [400, 0]
            },
            {
                "parameters": {
                    "resource": "message",
                    "operation": "delete",
                    "messageId": "={{$json.id}}"
                },
                "id": "gmail-delete",
                "name": "Gmail Delete",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [600, 0],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            }
        ],
        "connections": {
            "Webhook Trigger": { "main": [[{ "node": "Gmail Get Emails", "type": "main", "index": 0 }]] },
            "Gmail Get Emails": { "main": [[{ "node": "Pick Oldest 100", "type": "main", "index": 0 }]] },
            "Pick Oldest 100": { "main": [[{ "node": "Gmail Delete", "type": "main", "index": 0 }]] }
        },
        "settings": { 
            "executionOrder": "v1"
        }
    }
    
    try:
        print("Creating workflow...")
        res = requests.post(f"{base_url}/workflows", headers=headers, json=wf_data)
        if res.status_code != 200:
            print(f"Failed: {res.text}")
            return
        
        wf_id = res.json().get('id')
        print(f"Workflow created: {wf_id}")
        
        print("Activating...")
        requests.post(f"{base_url}/workflows/{wf_id}/activate", headers=headers)
        
        time.sleep(2)
        print("Triggering deletion of 100 oldest emails...")
        webhook_res = requests.post("https://eco.dxarte.org/webhook/delete-100-oldest")
        print(f"Trigger Status: {webhook_res.status_code}")
        
        if webhook_res.status_code == 200:
            print("Successfully started! Check n8n for progress.")
        else:
            print(f"Trigger failed: {webhook_res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
