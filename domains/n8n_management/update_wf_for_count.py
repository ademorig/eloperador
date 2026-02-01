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
            
            # 1. Update Gmail Search parameters
            for node in wf['nodes']:
                if node['name'] == 'Gmail Search':
                    node['parameters'] = {
                        'resource': 'message',
                        'operation': 'getAll',
                        'limit': 100, # Just a sample
                        'filters': {'q': 'label:inbox'}
                    }
            
            # 2. Update Format Output to be more careful
            for node in wf['nodes']:
                if node['name'] == 'Format Output':
                    node['parameters']['jsCode'] = """
let emails = [];
try {
  emails = $("Gmail Search").all();
} catch (e) {
  console.log("No email data");
}

let calendar = [];
try {
  calendar = $("Google Calendar Search").all();
} catch (e) {
  console.log("No calendar data");
}

return {
  summary: `Tienes ${emails.length} correos en tu bandeja de entrada.`,
  emailCount: emails.length,
  calendarCount: calendar.length,
  recentEmails: emails.slice(0, 5)
};
"""

            # 3. Clean up additional properties for PUT
            update_data = {
                "name": wf.get("name"),
                "nodes": wf.get("nodes"),
                "connections": wf.get("connections"),
                "settings": {
                    "executionOrder": "v1",
                    "availableInMCP": True
                }
            }
            
            for node in update_data['nodes']:
                keys_to_keep = ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials', 'webhookId', 'notes']
                keys_to_delete = [k for k in node.keys() if k not in keys_to_keep]
                for k in keys_to_delete:
                    del node[k]

            update_res = requests.put(url, headers=headers, json=update_data)
            print(f"Update Status: {update_res.status_code}")
            if update_res.status_code == 200:
                print("Successfully updated workflow for testing.")
            else:
                print(f"Update failed: {update_res.text}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
