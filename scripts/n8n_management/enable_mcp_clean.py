import requests
import os

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "qGTh7sd-DwFvTGHt660Kx"
    
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    url = f"https://eco.dxarte.org/api/v1/workflows/{wf_id}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            wf = response.json()
            
            # Bare minimum
            update_data = {
                "name": wf.get("name"),
                "nodes": wf.get("nodes"),
                "connections": wf.get("connections"),
                "settings": wf.get("settings", {})
            }
            update_data['settings']['availableInMCP'] = True
            
            # Remove properties from nodes that might be "additional"
            # Actually, nodes returned by GET might have 'userId', etc.
            for node in update_data['nodes']:
                # Keep only known properties
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            print(f"Sample node after cleaning: {update_data['nodes'][0]}")

            update_res = requests.put(url, headers=headers, json=update_data)
            print(f"Update Status: {update_res.status_code}")
            if update_res.status_code == 200:
                print("Successfully enabled availableInMCP.")
            else:
                print(f"Update failed: {update_res.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
