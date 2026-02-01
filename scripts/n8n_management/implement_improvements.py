import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
BASE_URL = "https://eco.dxarte.org/api/v1"
MAIN_WF_ID = "qGTh7sd-DwFvTGHt660Kx"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

def clean_up():
    print("Listing workflows...")
    res = requests.get(f"{BASE_URL}/workflows", headers=headers).json()
    workflows = res.get('data', [])
    
    for wf in workflows:
        wf_id = wf['id']
        wf_name = wf['name']
        
        # 1. Consolidate Agents (Delete duplicates or temp ones)
        if wf_id == MAIN_WF_ID:
            continue
            
        if wf_name in ["Radiology_Shift_Organizer_Agent", "Radiology_Direct_Check", "Urgent_Task_Checker_Final", "Gmail_Auto_Cleanup_Oldest_250"]:
            print(f"Deleting workflow: {wf_name} (ID: {wf_id})")
            requests.delete(f"{BASE_URL}/workflows/{wf_id}", headers=headers)

def create_error_handler():
    print("Creating Error Handler workflow...")
    error_wf = {
        "name": "Global_Error_Handler_Radiology",
        "nodes": [
            {
                "parameters": {},
                "name": "Error Trigger",
                "type": "n8n-nodes-base.errorTrigger",
                "typeVersion": 1,
                "position": [0, 0]
            },
            {
                "parameters": {
                    "jsCode": "return {\n  msg: `🚨 Error en workflow: ${$json.workflow.name}`,\n  error: $json.execution.error.message,\n  id: $json.execution.id\n};"
                },
                "name": "Format Error",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1,
                "position": [250, 0]
            }
        ],
        "connections": {
            "Error Trigger": { "main": [[{ "node": "Format Error", "type": "main", "index": 0 }]] }
        },
        "settings": { "executionOrder": "v1" }
    }
    res = requests.post(f"{BASE_URL}/workflows", headers=headers, json=error_wf).json()
    return res.get('id')

def update_main_wf(error_wf_id):
    print(f"Updating Main Workflow {MAIN_WF_ID} with Normalization and Error Handler...")
    wf = requests.get(f"{BASE_URL}/workflows/{MAIN_WF_ID}", headers=headers).json()
    
    # 2. Add Normalization Node (Set)
    # The current workflow goes: Webhook -> [Tools...] -> (Format Output)
    # Wait, the current version is simplified: Webhook -> Tools -> Output.
    # Let's insert a "Normalize Input" node.
    
    normalization_node = {
        "parameters": {
            "keepOnlySet": True,
            "values": {
                "string": [
                    {
                        "name": "userQuery",
                        "value": "={{ $json.body.input || $json.chatInput || 'Revisar urgencias' }}"
                    }
                ]
            },
            "options": {}
        },
        "id": "norm-1",
        "name": "Normalize Input",
        "type": "n8n-nodes-base.set",
        "typeVersion": 1,
        "position": [-900, 32]
    }
    
    # Update AI Agent to use userQuery
    for node in wf['nodes']:
        if node['name'] == 'AI Agent':
            node['parameters']['text'] = "={{ $json.userQuery }}"
            
    # Insert normalization node after Webhook
    wf['nodes'].append(normalization_node)
    
    # Relink: MCP Trigger -> Normalize Input -> AI Agent
    if 'MCP Trigger' in wf['connections']:
        wf['connections']['MCP Trigger']['main'] = [[{"node": "Normalize Input", "type": "main", "index": 0}]]
    
    wf['connections']['Normalize Input'] = {
        "main": [[{"node": "AI Agent", "type": "main", "index": 0}]]
    }
    
    # 3. Add Error Handler
    if error_wf_id:
        wf['settings']['errorWorkflow'] = error_wf_id
    
    requests.put(f"{BASE_URL}/workflows/{MAIN_WF_ID}", headers=headers, json=wf)
    requests.post(f"{BASE_URL}/workflows/{MAIN_WF_ID}/activate", headers=headers)
    print("Main workflow updated and reactivated.")

if __name__ == "__main__":
    clean_up()
    err_id = create_error_handler()
    update_main_wf(err_id)
