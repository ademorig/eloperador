import requests
import os

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "KC4Tkg1MqFfhyef7"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
        if res.status_code == 200:
            wf = res.json()
            # Change the path
            for node in wf['nodes']:
                if node['type'] == 'n8n-nodes-base.webhook':
                    node['parameters']['path'] = 'clean-inbox-batch'
            
            # Update
            update_data = {
                "name": wf.get("name"),
                "nodes": wf.get("nodes"),
                "connections": wf.get("connections"),
                "settings": {"executionOrder": "v1"}
            }
            # Clean nodes
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
            print("Path updated to clean-inbox-batch")
            
            requests.post(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}/activate", headers=headers)
            print("Activated")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
