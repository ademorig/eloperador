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
            
            for node in wf['nodes']:
                if node['name'] == 'Gmail Search':
                    node['parameters']['limit'] = 500 # Increase limit
            
            for node in wf['nodes']:
                if node['name'] == 'Format Output':
                    node['parameters']['jsCode'] = """
let emails = [];
try {
  emails = $("Gmail Search").all();
} catch (e) {}

return {
  summary: `Tienes ${emails.length} correos en tu bandeja de entrada de Gmail.`
};
"""

            update_data = {
                "name": wf.get("name"),
                "nodes": wf.get("nodes"),
                "connections": wf.get("connections"),
                "settings": {"executionOrder": "v1", "availableInMCP": True}
            }
            
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            requests.put(url, headers=headers, json=update_data)
            print("Successfully updated workflow with higher limit.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
