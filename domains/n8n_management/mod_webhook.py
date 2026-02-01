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
    response = requests.get(f"{BASE_URL}/workflows/{workflow_id}", headers=headers)
    return response.json()

def update_workflow(workflow_id, data):
    response = requests.put(f"{BASE_URL}/workflows/{workflow_id}", headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    wf = get_workflow(WORKFLOW_ID)
    
    # Set Webhook to respond with last node
    nodes = wf.get('nodes', [])
    webhook_node = next((n for n in nodes if n['type'] == 'n8n-nodes-base.webhook'), None)
    if webhook_node:
        webhook_node['parameters']['responseMode'] = 'lastNode'
    
    update_data = {
        "name": wf.get('name'),
        "nodes": nodes,
        "connections": wf['connections'],
        "settings": wf.get('settings', {})
    }
    
    print("Updating workflow to respond with last node...")
    update_workflow(WORKFLOW_ID, update_data)
    
    print("Re-activating workflow...")
    requests.post(f"{BASE_URL}/workflows/{WORKFLOW_ID}/activate", headers=headers)
    print("Done.")
