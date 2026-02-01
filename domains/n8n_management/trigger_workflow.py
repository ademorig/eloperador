import requests
import json

def main():
    url = "https://eco.dxarte.org/webhook/radiology-mcp"
    
    payload = {
        "input": "Dime el número de correos en mi bandeja de entrada de Gmail."
    }
    
    try:
        print(f"Triggering workflow at {url}...")
        response = requests.post(url, json=payload)
        print(f"Status: {response.status_code}")
        print("\n--- RESULT ---")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()
