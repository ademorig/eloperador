import requests

def test_trigger(url):
    print(f"Testing {url}...")
    for method in [requests.get, requests.post]:
        try:
            r = method(url)
            print(f"{method.__name__.upper()} {url} -> {r.status_code}")
            if r.status_code != 404:
                print(r.text[:200])
        except Exception as e:
            print(f"Error {method.__name__.upper()}: {e}")

if __name__ == "__main__":
    test_trigger("https://eco.dxarte.org/webhook/clean-inbox-batch")
    test_trigger("https://eco.dxarte.org/webhook/delete-100-oldest")
    test_trigger("https://eco.dxarte.org/webhook/radiology-mcp")
