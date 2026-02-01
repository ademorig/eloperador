import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
BASE_URL = "https://eco.dxarte.org/api/v1"
WORKFLOW_ID = "qGTh7sd-DwFvTGHt660Kx"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def get_workflow(workflow_id):
    return requests.get(f"{BASE_URL}/workflows/{workflow_id}", headers=headers).json()

def update_workflow(workflow_id, data):
    return requests.put(f"{BASE_URL}/workflows/{workflow_id}", headers=headers, json=data).json()

if __name__ == "__main__":
    wf = get_workflow(WORKFLOW_ID)
    
    # Create a simple direct workflow: Webhook -> Google Calendar -> Gmail -> Code -> Webhook Response
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "radiology-direct",
                "responseMode": "lastNode",
                "options": {}
            },
            "id": "node-1",
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [0, 0]
        },
        {
            "parameters": {
                "operation": "list",
                "calendar": "primary",
                "filters": {
                    "timeMin": "={{ $now.startOfDay().toISO() }}",
                    "timeMax": "={{ $now.plus(1, 'day').endOfDay().toISO() }}"
                }
            },
            "id": "node-2",
            "name": "Calendar",
            "type": "n8n-nodes-base.googleCalendar",
            "typeVersion": 1,
            "position": [200, 0],
            "credentials": wf['nodes'][3 if len(wf['nodes'])>3 else 0].get('credentials', {}) # Try to reuse credentials 
        },
        {
            "parameters": {
                "operation": "getAll",
                "filters": {
                    "q": "is:unread (label:urgent OR STAT)"
                }
            },
            "id": "node-3",
            "name": "Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2,
            "position": [400, 0],
            "credentials": wf['nodes'][4 if len(wf['nodes'])>4 else 0].get('credentials', {}) # Try to reuse credentials
        }
    ]
    
    # Extract credentials properly from the original workflow
    # Calendar node was '5ebe5a06-ab78-4acb-a852-d28d537f13ef'
    # Gmail node was '4c315159-f496-496c-817e-76b575b5c4a7'
    cal_creds = next((n['credentials'] for n in wf['nodes'] if n['name'] == 'Google Calendar Search'), {})
    gmail_creds = next((n['credentials'] for n in wf['nodes'] if n['name'] == 'Gmail Search'), {})
    
    nodes[1]['credentials'] = cal_creds
    nodes[2]['credentials'] = gmail_creds
    
    connections = {
        "Webhook": {"main": [[{"node": "Calendar", "type": "main", "index": 0}]]},
        "Calendar": {"main": [[{"node": "Gmail", "type": "main", "index": 0}]]}
    }
    
    update_data = {
        "name": "Radiology_Direct_Check",
        "nodes": nodes,
        "connections": connections,
        "settings": {"executionOrder": "v1"}
    }
    
    print("Creating direct check workflow...")
    # I'll create a NEW workflow instead of overwriting the user's one
    res = requests.post(f"{BASE_URL}/workflows", headers=headers, json=update_data).json()
    new_id = res.get('id')
    print(f"New Workflow ID: {new_id}")
    
    if new_id:
        print("Activating...")
        requests.post(f"{BASE_URL}/workflows/{new_id}/activate", headers=headers)
        print(f"Trigger URL: https://eco.dxarte.org/webhook/radiology-direct")
