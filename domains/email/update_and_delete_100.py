import requests
import time

def main():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
    wf_id = "KC4Tkg1MqFfhyef7"
    headers = {
        "X-N8N-API-KEY": token,
        "Content-Type": "application/json"
    }
    
    # 1. Get current workflow
    res = requests.get(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers)
    wf = res.json()
    
    # 2. Update nodes
    for node in wf['nodes']:
        if node['id'] == 'gmail-get' or node['name'] == 'Gmail Get Emails':
            node['parameters']['limit'] = 500 # Fetch more to pick the oldest of the batch
        if node['id'] == 'sort-node' or node['name'] == 'Pick Oldest 200':
            node['name'] = 'Pick Oldest 100'
            node['parameters']['jsCode'] = 'return $input.all().reverse().slice(0, 100);'
    
    # Clean for update
    update_data = {
        "name": "Antigravity_Batch_Delete_Oldest_100",
        "nodes": wf['nodes'],
        "connections": wf['connections'],
        "settings": wf['settings']
    }
    
    # Remove extra fields that API might reject
    for node in update_data['nodes']:
        for key in list(node.keys()):
            if key not in ['id', 'name', 'type', 'typeVersion', 'position', 'parameters', 'credentials']:
                del node[key]

    print("Updating workflow...")
    res = requests.put(f"https://eco.dxarte.org/api/v1/workflows/{wf_id}", headers=headers, json=update_data)
    print(f"Update Status: {res.status_code}")
    
    if res.status_code == 200:
        # Trigger it
        time.sleep(2)
        print("Triggering deletion...")
        r = requests.post("https://eco.dxarte.org/webhook/clean-inbox-batch")
        print(f"Trigger Status: {r.status_code}")
        if r.status_code == 200:
            print("Successfully started the deletion of 100 oldest emails.")
        else:
            print(f"Trigger failed: {r.text}")

if __name__ == "__main__":
    main()
