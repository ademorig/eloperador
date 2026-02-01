import requests
import json

def main():
    url = "https://eco.dxarte.org/webhook/clean-inbox-batch"
    
    try:
        print(f"Triggering deletion at {url}...")
        response = requests.post(url)
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
