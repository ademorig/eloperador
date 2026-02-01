import requests
import json
import time

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
BASE_URL = "https://eco.dxarte.org/api/v1"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

wf_data = {
    "name": "Urgent_Task_Checker_Final",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "check-urgent-tasks",
                "responseMode": "lastNode",
                "options": {}
            },
            "name": "Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [0, 0]
        },
        {
            "parameters": {
                "operation": "list",
                "calendar": "primary",
                "filters": {
                    "timeMin": "2026-01-30T00:00:00Z",
                    "timeMax": "2026-02-01T23:59:59Z"
                }
            },
            "name": "Calendar",
            "type": "n8n-nodes-base.googleCalendar",
            "typeVersion": 1,
            "position": [200, -50],
            "credentials": {"googleCalendarOAuth2Api": {"id": "70NbzbTcPExxryMN"}}
        },
        {
            "parameters": {
                "operation": "getAll",
                "filters": {
                    "q": "is:unread (urgent OR STAT OR ASAP)"
                }
            },
            "name": "Gmail",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2,
            "position": [200, 150],
            "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
        },
        {
            "parameters": {
                "jsCode": "const cal = $node['Calendar'].json;\nconst emails = $node['Gmail'].json;\nreturn {\n  urgencias: Array.isArray(emails) ? emails.map(e => e.subject) : [emails.subject].filter(Boolean),\n  eventos: Array.isArray(cal) ? cal.map(c => ({ summary: c.summary, start: c.start.dateTime })) : [cal].map(c => ({ summary: c.summary, start: c.start.dateTime })).filter(e => e.summary)\n};"
            },
            "name": "Merge",
            "type": "n8n-nodes-base.code",
            "typeVersion": 1,
            "position": [450, 50]
        }
    ],
    "connections": {
        "Webhook": { "main": [[{ "node": "Calendar", "type": "main", "index": 0 }, { "node": "Gmail", "type": "main", "index": 0 }]] },
        "Calendar": { "main": [[{ "node": "Merge", "type": "main", "index": 0 }]] },
        "Gmail": { "main": [[{ "node": "Merge", "type": "main", "index": 0 }]] }
    },
    "settings": { "executionOrder": "v1" }
}

print("Creating workflow...")
res = requests.post(f"{BASE_URL}/workflows", headers=headers, json=wf_data).json()
wf_id = res.get('id')
print(f"Workflow ID: {wf_id}")

if wf_id:
    print("Activating...")
    requests.post(f"{BASE_URL}/workflows/{wf_id}/activate", headers=headers)
    
    # Wait for registration
    time.sleep(2)
    
    print("Triggering...")
    trigger_url = "https://eco.dxarte.org/webhook/check-urgent-tasks"
    resp = requests.post(trigger_url, json={})
    print(f"Result Status: {resp.status_code}")
    print("Result Body:")
    print(resp.text)
