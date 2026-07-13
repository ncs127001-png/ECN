import requests
import time
import os

BASE_URL = "http://127.0.0.1:5000"

def test_centinela():
    print("\n[TEST] Centinela Status...")
    try:
        r = requests.get(f"{BASE_URL}/centinela_status")
        print(r.json())
    except Exception as e:
        print(f"FAILED: {e}")

def test_search():
    print("\n[TEST] Search Files (pattern='api')...")
    try:
        r = requests.post(f"{BASE_URL}/search_files", json={"pattern": "api"})
        print(r.json())
    except Exception as e:
        print(f"FAILED: {e}")

def test_fragment():
    print("\n[TEST] Fragment Upload...")
    try:
        files = {'file': ('test.txt', 'This is a test fragment content for the API.')}
        r = requests.post(f"{BASE_URL}/fragment", files=files)
        print(r.json())
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    print("Verifying Tier 2 Endpoints...")
    test_centinela()
    test_search()
    test_fragment()
