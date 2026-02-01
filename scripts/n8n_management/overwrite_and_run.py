import requests
import json

API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmNDI1ODIxNC1jMDM5LTQwYTctYWMzYy01MWQxZTBiNWY0ZTgiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwiaWF0IjoxNzY5ODMwMTc4fQ.ptyrZ_3zxYioT8wt_DE0BarK5QSRjAmYNdHs_fFaHgI"
BASE_URL = "https://eco.dxarte.org/api/v1"
WORKFLOW_ID = "qGTh7sd-DwFvTGHt660Kx"

headers = {
    "X-N8N-API-KEY": API_KEY,
    "Content-Type": "application/json"
}

wf_data = {
    "name": "Radiology_Shift_Organizer_Agent",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "radiology-mcp",
                "responseMode": "lastNode",
                "options": {}
            },
            "name": "MCP Trigger",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [0, 0]
        },
        {
            "parameters": {
                "operation": "list",
                "calendar": "primary",
                "filters": {
                    "timeMin": "2026-01-31T00:00:00Z",
                    "timeMax": "2026-01-31T23:59:59Z"
                }
            },
            "name": "Google Calendar Search",
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
            "name": "Gmail Search",
            "type": "n8n-nodes-base.gmail",
            "typeVersion": 2,
            "position": [200, 150],
            "credentials": {"gmailOAuth2": {"id": "Fhvq4vOWbvQhrvvi"}}
        },
        {
            "parameters": {
                "jsCode": "const cal = $node['Google Calendar Search'].json;\nconst emails = $node['Gmail Search'].json;\nreturn {\n  urgencias: Array.isArray(emails) ? emails.map(e => ({subject: e.subject, from: e.from.value[0].address})) : (emails.subject ? [{subject: emails.subject}] : []),\n  eventos: Array.isArray(cal) ? cal.map(c => ({ summary: c.summary, start: c.start.dateTime })) : (cal.summary ? [{ summary: cal.summary, start: cal.start.dateTime }] : [])\n};"
            },
            "name": "Format Output",
            "type": "n8n-nodes-base.code",
            "typeVersion": 1,
            "position": [450, 50]
        }
    ],
    "connections": {
        "MCP Trigger": { "main": [[{ "node": "Google Calendar Search", "type": "main", "index": 0 }, { "node": "Gmail Search", "type": "main", "index": 0 }]] },
        "Google Calendar Search": { "main": [[{ "node": "Format Output", "type": "main", "index": 0 }]] },
        "Gmail Search": { "main": [[{ "node": "Format Output", "type": "main", "index": 0 }]] }
    },
    "settings": { "executionOrder": "v1" }
}

print("Overwriting existing functional workflow...")
requests.put(f"{BASE_URL}/workflows/{WORKFLOW_ID}", headers=headers, json=wf_data)
requests.post(f"{BASE_URL}/workflows/{WORKFLOW_ID}/activate", headers=headers)
print("Done. Triggering...")

resp = requests.post("https://eco.dxarte.org/webhook/radiology-mcp", json={})
print(f"Status: {resp.status_code}")
print(f"Body: {resp.text}")
