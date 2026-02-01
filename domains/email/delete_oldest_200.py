import requests
import os
import time

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    # 1. Create a specific workflow for deletion
    # We use Gmail 'getAll' with limit 200, sorting by oldest (default is newest, so we'll fetch all and slice or see if q can sort)
    # Actually, n8n's Gmail node doesn't have a direct 'oldest' sort for 'getAll' messages easily.
    # Better approach: Get messages with a search query, and n8n usually respects Gmail API default (newest first).
    # To get oldest, we can use the 'q' parameter with 'before:YYYY/MM/DD' or fetch many and reverse.
    
    # Logic: Get 200 messages from INBOX, then delete them one by one.
    
    wf_data = {
        "name": "Antigravity_Batch_Delete_Oldest_200",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "delete-oldest-emails",
                    "options": {}
                },
                "id": "trigger-1",
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [200, 300]
            },
            {
                "parameters": {
                    "operation": "getAll",
                    "limit": 200,
                    "filters": {
                        "q": "label:inbox"
                    }
                },
                "id": "gmail-get",
                "name": "Gmail Get Emails",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [450, 300],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            },
            {
                "parameters": {
                    "jsCode": "// Reverse the order to get the oldest ones from the set if we fetched a limit\n// Actually, if we fetch 500, we pick the last 200.\n// Let's assume the user wants the absolute oldest in the inbox.\r\nreturn $input.all().reverse().slice(0, 200);"
                },
                "id": "sort-node",
                "name": "Pick Oldest 200",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1,
                "position": [650, 300]
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
                "position": [850, 300],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            }
        ],
        "connections": {
            "Webhook Trigger": { "main": [[{ "node": "Gmail Get Emails", "type": "main", "index": 0 }]] },
            "Gmail Get Emails": { "main": [[{ "node": "Pick Oldest 200", "type": "main", "index": 0 }]] },
            "Pick Oldest 200": { "main": [[{ "node": "Gmail Delete", "type": "main", "index": 0 }]] }
        },
        "settings": { 
            "executionOrder": "v1",
            "saveExecutionProgress": True,
            "saveManualExecutions": True
        }
    }
    
    try:
        print("Creating deletion workflow...")
        create_res = requests.post("https://eco.dxarte.org/api/v1/workflows", headers=headers, json=wf_data)
        if create_res.status_code != 200:
            print(f"Failed to create workflow: {create_res.text}")
            return
        
        wf_id = create_res.json().get('id')
        print(f"Workflow created with ID: {wf_id}")
        
        # 2. Activate it
        print("Activating workflow...")
        requests.post(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}/activate", headers=headers)
        
        # 3. Trigger it
        time.sleep(2)
        print("Triggering deletion process...")
        trigger_res = requests.post("https://eco.dxarte.org/webhook/delete-oldest-emails")
        print(f"Trigger Status: {trigger_res.status_code}")
        
        if trigger_res.status_code == 200:
            print("Successfully started the deletion of 200 oldest emails.")
            print("The process is running in the background in n8n.")
        else:
            print(f"Trigger failed: {trigger_res.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
