import requests
import time

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "qGTh7sd-DwFvTGHt660Kx"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    print(f"Activating workflow {wf_id}...")
    try:
        # Step 1: Activate the workflow
        # The public API doesn't have a direct 'activate' endpoint in documentation, 
        # but usually it's POST /workflows/{id}/activate or just updating the 'active' property.
        # However, looking at previous scripts, POST /workflows/{wf_id}/activate was used.
        
        # Let's try to update the workflow to 'active': true if the POST fails, 
        # but let's try the POST first.
        activate_res = requests.post(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}/activate", headers=headers)
        print(f"Activation Status: {activate_res.status_code}")
        
        if activate_res.status_code != 200:
            # Try setting active to True via PUT
            print("Try setting active: True via PUT...")
            wf_res = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
            if wf_res.status_code == 200:
                wf = wf_res.json()
                wf['active'] = True
                # Clean nodes as before
                for node in wf['nodes']:
                    keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                    keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                    for k in keys_to_delete:
                        del node[k]
                
                # Clean settings
                current_settings = wf.get("settings", {})
                allowed_settings = ["executionOrder", "availableInMCP", "saveExecutionProgress", "saveManualExecutions", "callerPolicy", "errorWorkflow"]
                clean_settings = {k: v for k, v in current_settings.items() if k in allowed_settings}
                
                update_data = {
                    "name": wf.get("name"),
                    "nodes": wf.get("nodes"),
                    "connections": wf.get("connections"),
                    "settings": clean_settings,
                    "active": True
                }
                put_res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
                print(f"PUT Activation Status: {put_res.status_code}")
        
        time.sleep(2)
        
        # Step 2: Trigger deletion
        print("Triggering deletion...")
        trigger_res = requests.post("https://eco.dxarte.org/webhook/radiology-mcp")
        print(f"Trigger Status: {trigger_res.status_code}")
        print(trigger_res.text)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
