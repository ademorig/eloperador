import requests
import os

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
            
            nodes = wf['nodes']
            for node in nodes:
                if node['id'] == "code-sort-batch-unique" or node['name'] == "Pick 200 Oldest" or node['name'] == "Pick 150 Oldest":
                    node['name'] = "Pick 150 Oldest"
                    node['parameters']['jsCode'] = 'return $input.all().reverse().slice(0, 150);'
                
                if node['name'] == 'Format Output':
                    node['parameters']['jsCode'] = "return { summary: 'Se ha iniciado el borrado de los 150 correos más antiguos.' };"

            # Clean settings specifically
            current_settings = wf.get("settings", {})
            allowed_settings = ["executionOrder", "availableInMCP", "saveExecutionProgress", "saveManualExecutions", "callerPolicy", "errorWorkflow"]
            clean_settings = {k: v for k, v in current_settings.items() if k in allowed_settings}
            clean_settings["availableInMCP"] = True # Ensure it stays enabled

            update_data = {
                "name": wf.get("name"),
                "nodes": nodes,
                "connections": wf.get("connections"),
                "settings": clean_settings
            }
            
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
            print(f"Update Status: {res.status_code}")
            if res.status_code == 200:
                print("Successfully updated workflow to 150 emails limit.")
            else:
                print(res.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
