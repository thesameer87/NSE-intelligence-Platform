import urllib.request
import urllib.error
import json
import time
import os
from dotenv import load_dotenv

# Load env to get DB URL
load_dotenv(".env")

BASE_URL = "http://localhost:8000"
INTERNAL_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-internal-token")
HEADERS = {"X-Internal-Token": INTERNAL_TOKEN}

def make_request(method, url, headers=None, data=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return e.code, body

def print_section(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def run_validations():
    print_section("1. Live Reload API Test")
    status_code, data = make_request("POST", f"{BASE_URL}/api/v1/internal/reload-models", headers=HEADERS)
    print(f"Status Code: {status_code}")
    if status_code == 200:
        print(f"Success: {data.get('success')}")
        print(f"Reload Time (ms): {data.get('reload_time_ms')}")
        print(f"Last Reload Status: {data.get('last_reload_status')}")
    else:
        print(f"Response: {data}")

    print_section("2. Unauthorized Access Test")
    status_missing, _ = make_request("POST", f"{BASE_URL}/api/v1/internal/reload-models")
    print(f"Missing Header Status: {status_missing}")
    
    status_invalid, _ = make_request("POST", f"{BASE_URL}/api/v1/internal/reload-models", headers={"X-Internal-Token": "wrong-token"})
    print(f"Invalid Header Status: {status_invalid}")

    print_section("3. Rollback Validation (Corrupt Artifact)")
    status_latest, data = make_request("GET", f"{BASE_URL}/api/v1/prediction/models/latest")
    models = data.get("models", [])
    
    if models:
        first_model = models[0]
        artifact_path = first_model["artifact_path"]
        print(f"Temporarily corrupting {artifact_path}...")
        
        # Read original
        try:
            with open(artifact_path, "rb") as f:
                original_data = f.read()
        except Exception as e:
            print(f"Error reading artifact: {e}")
            original_data = None
            
        if original_data:
            # Corrupt it
            with open(artifact_path, "wb") as f:
                f.write(b"corrupted data")
                
            # Trigger reload
            status_fail, body_fail = make_request("POST", f"{BASE_URL}/api/v1/internal/reload-models", headers=HEADERS)
            print(f"Status Code after corruption: {status_fail}")
            print(f"Response: {body_fail}")
            
            # Restore it
            with open(artifact_path, "wb") as f:
                f.write(original_data)
            print("Restored original artifact.")
    else:
        print("No models found in DB.")

    print_section("4. Runtime State Validation")
    status_state, state_data = make_request("GET", f"{BASE_URL}/api/v1/prediction/models/latest")
    print(f"Last Reload Status: {state_data.get('last_reload_status')}")
    print(f"Last Reload Time: {state_data.get('last_reload_time')}")

    print_section("5. Prometheus Validation")
    try:
        req = urllib.request.Request(f"{BASE_URL}/metrics/prometheus", method="GET")
        with urllib.request.urlopen(req) as response:
            text = response.read().decode()
            lines = text.splitlines()
            found_metrics = [line for line in lines if "model_reload_" in line and not line.startswith("#")]
            for m in found_metrics:
                print(m)
    except urllib.error.HTTPError as e:
        print(f"Failed to fetch metrics: {e.code}")


if __name__ == "__main__":
    run_validations()
