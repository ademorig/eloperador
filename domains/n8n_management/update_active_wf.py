import requests
import os

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "qGTh7sd-DwFvTGHt660Kx" # The radiology one that works
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
        if response.status_code == 200:
            wf = response.json()
            
            # Add deletion logic to THIS workflow
            # 1. Add Gmail nodes for deletion
            
            gmail_get = {
                "parameters": {
                    "operation": "getAll",
                    "limit": 500,
                    "filters": {"q": "label:inbox"}
                },
                "id": "gmail-get-batch",
                "name": "Gmail Get Batch",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [200, 100],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            }
            
            code_sort = {
                "parameters": {
                    "jsCode": "return $input.all().reverse().slice(0, 200);"
                },
                "id": "code-sort-batch",
                "name": "Pick 200 Oldest",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1,
                "position": [400, 100]
            }
            
            gmail_delete = {
                "parameters": {
                    "resource": "message",
                    "operation": "delete",
                    "messageId": "={{$json.id}}"
                },
                "id": "gmail-delete-batch",
                "name": "Delete Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [600, 100],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            }
            
            wf['nodes'].extend([gmail_get, code_sort, gmail_delete])
            
            # 2. Add connections
            if 'Gmail Get Batch' not in wf['connections']:
                wf['connections']['Gmail Get Batch'] = {"main": [[]]}
            if 'Pick 200 Oldest' not in wf['connections']:
                wf['connections']['Pick 200 Oldest'] = {"main": [[]]}
            
            wf['connections']['MCP Trigger']['main'][0].append({"node": "Gmail Get Batch", "type": "main", "index": 0})
            wf['connections']['Gmail Get Batch'] = {"main": [[{"node": "Pick 200 Oldest", "type": "main", "index": 0}]]}
            wf['connections']['Pick 200 Oldest'] = {"main": [[{"node": "Delete Email", "type": "main", "index": 0}]]}
            
            # Update Format Output to say started
            for node in wf['nodes']:
                if node['name'] == 'Format Output':
                    node['parameters']['jsCode'] = "return { summary: 'Se ha iniciado el borrado de los 200 correos más antiguos.' };"

            # Update
            update_data = {
                "name": wf.get("name"),
                "nodes": wf.get("nodes"),
                "connections": wf.get("connections"),
                "settings": wf.get("settings", {})
            }
            # Clean nodes
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
            print(f"Update Result: {res.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
