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
    
    # Filter nodes to remove problematic ones if any
    nodes = wf.get('nodes', [])
    # Remove 'Window Buffer Memory' if it's causing activation issues
    nodes = [n for n in nodes if n['type'] != '@n8n/n8n-nodes-langchain.memoryWindowBuffer']
    
    ai_agent_node = next((n for n in nodes if n['name'] == 'AI Agent'), None)
    if ai_agent_node:
        ai_agent_node['parameters']['text'] = "={{ $json.body.input }}"
    
    # Fix connections
    connections = wf.get('connections', {})
    # Ensure tool connections
    connections['Google Calendar Search'] = {
        "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
    }
    connections['Gmail Search'] = {
        "ai_tool": [[{"node": "AI Agent", "type": "ai_tool", "index": 0}]]
    }
    
    # Remove the problematic memory connection if it exists
    if 'Window Buffer Memory' in connections:
        del connections['Window Buffer Memory']

    # Essential settings only
    settings = {
        "executionOrder": "v1"
    }
    
    update_data = {
        "name": wf.get('name'),
        "nodes": nodes,
        "connections": connections,
        "settings": settings
    }
    
    print("Updating workflow...")
    result = update_workflow(WORKFLOW_ID, update_data)
    print(f"Update Result: {json.dumps(result, indent=2)}")

    if 'id' in result:
        print("Activating workflow...")
        activate_res = requests.post(f"{BASE_URL}/workflows/{WORKFLOW_ID}/activate", headers=headers)
        print(f"Activation Status: {activate_res.status_code}")
        print(f"Activation Body: {activate_res.text}")
