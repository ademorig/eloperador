import requests
import json

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "qGTh7sd-DwFvTGHt660Kx"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
        if res.status_code == 200:
            wf = res.json()
            
            # Old name: Pick 200 Oldest
            # New name: Pick 150 Oldest
            
            connections = wf['connections']
            
            # 1. Update source node names in connections
            if 'Pick 200 Oldest' in connections:
                connections['Pick 150 Oldest'] = connections.pop('Pick 200 Oldest')
                print("Renamed connection source from Pick 200 Oldest to Pick 150 Oldest")
            
            # 2. Update destination node names in connections
            for source_node in connections:
                main_conns = connections[source_node].get('main', [])
                for target_level in main_conns:
                    for target in target_level:
                        if target['node'] == 'Pick 200 Oldest':
                            target['node'] = 'Pick 150 Oldest'
                            print(f"Updated connection target in {source_node} to Pick 150 Oldest")

            # Clean nodes and settings for update
            for node in wf['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]
            
            current_settings = wf.get("settings", {})
            allowed_settings = ["executionOrder", "availableInMCP", "saveExecutionProgress", "saveManualExecutions", "callerPolicy", "errorWorkflow"]
            clean_settings = {k: v for k, v in current_settings.items() if k in allowed_settings}

            update_data = {
                "name": wf.get("name"),
                "nodes": wf['nodes'],
                "connections": connections,
                "settings": clean_settings
            }
            
            put_res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
            print(f"Update Result: {put_res.status_code}")
            
            if put_res.status_code == 200:
                print("Triggering deletion...")
                trigger_res = requests.post("https://eco.dxarte.org/webhook/radiology-mcp")
                print(f"Trigger Status: {trigger_res.status_code}")
                print(trigger_res.text)

        else:
            print(res.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
