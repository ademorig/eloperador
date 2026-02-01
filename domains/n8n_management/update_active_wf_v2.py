import requests
import os
import json

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "qGTh7sd-DwFvTGHt660Kx"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
        if response.status_code == 200:
            wf = response.json()
            
            # Use real node IDs if possible or just fresh ones
            new_id_1 = "gmail-get-batch-unique"
            new_id_2 = "code-sort-batch-unique"
            new_id_3 = "gmail-delete-batch-unique"
            
            nodes = wf['nodes']
            nodes.append({
                "parameters": {
                    "operation": "getAll",
                    "limit": 500,
                    "filters": {"q": "label:inbox"}
                },
                "id": new_id_1,
                "name": "Gmail Get Batch",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [200, 100],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            })
            nodes.append({
                "parameters": {
                    "jsCode": "return $input.all().reverse().slice(0, 200);"
                },
                "id": new_id_2,
                "name": "Pick 200 Oldest",
                "type": "n8n-nodes-base.code",
                "typeVersion": 1,
                "position": [400, 100]
            })
            nodes.append({
                "parameters": {
                    "resource": "message",
                    "operation": "delete",
                    "messageId": "={{$json.id}}"
                },
                "id": new_id_3,
                "name": "Delete Email",
                "type": "n8n-nodes-base.gmail",
                "typeVersion": 2,
                "position": [600, 100],
                "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
            })
            
            connections = wf['connections']
            # Add to MCP Trigger
            if "MCP Trigger" in connections:
                connections["MCP Trigger"]["main"][0].append({"node": "Gmail Get Batch", "type": "main", "index": 0})
            
            connections["Gmail Get Batch"] = {"main": [[{"node": "Pick 200 Oldest", "type": "main", "index": 0}]]}
            connections["Pick 200 Oldest"] = {"main": [[{"node": "Delete Email", "type": "main", "index": 0}]]}
            
            for node in nodes:
                if node['name'] == 'Format Output':
                    node['parameters']['jsCode'] = "return { summary: 'Se ha iniciado el borrado de los 200 correos más antiguos.' };"

            update_data = {
                "name": wf.get("name"),
                "nodes": nodes,
                "connections": connections,
                "settings": {"executionOrder": "v1", "availableInMCP": True}
            }
            
            # Final cleaning
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
            print(f"Update Status: {res.status_code}")
            if res.status_code != 200:
                print(res.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
