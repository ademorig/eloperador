import requests
import json

URL = "https://eco.dxarte.org/webhook/radiology-mcp"
data = {
    "input": "Revisa mis correos de Gmail buscando urgencias y dime si tengo huecos en el calendario para el 31 de enero de 2026 (mañana)."
}

print(f"Triggering webhook at {URL}...")
response = requests.post(URL, json=data)

print(f"Status Code: {response.status_code}")
try:
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))
except:
    print(response.text)
