import urllib.request
import urllib.error
import json
import asyncio
import websockets
import os
from dotenv import load_dotenv

# Load env to get DB URL
load_dotenv(".env")

RENDER_URL = "https://nse-intelligence-mk64.onrender.com"
VERCEL_URL = "https://nse-intelligence-platform.vercel.app"
WS_URL = "wss://nse-intelligence-mk64.onrender.com/api/v1/ws"
INTERNAL_TOKEN = os.getenv("INTERNAL_API_TOKEN", "dev-internal-token")

def print_header(title):
    print(f"\n{'='*50}\n{title}\n{'='*50}")

def make_request(method, url, headers=None):
    if headers is None:
        headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            try:
                data = json.loads(response.read().decode())
                return response.status, data
            except json.JSONDecodeError:
                return response.status, "Non-JSON response"
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return 0, str(e)

async def validate_websocket():
    print_header("3. WebSocket Connectivity & Runtime State Validation")
    try:
        async with websockets.connect(WS_URL) as ws:
            print("Connected to WebSocket.")
            
            # Subscribe to NIFTY 50
            subscribe_msg = json.dumps({"action": "subscribe", "symbol": "NIFTY 50"})
            await ws.send(subscribe_msg)
            print("Sent subscription request.")
            
            # Wait for prediction_update
            for _ in range(5):
                msg = await asyncio.wait_for(ws.recv(), timeout=10)
                data = json.loads(msg)
                event_type = data.get("event")
                if event_type == "prediction_update":
                    print("Received prediction_update event!")
                    payload = data.get("data", {})
                    print(f"Prediction Runtime Enabled: {payload.get('prediction_runtime_enabled')}")
                    print(f"Available Models: {payload.get('available_models')}")
                    return True
                elif event_type == "market_update":
                    print("Received market_update event. Waiting for prediction...")
            
            print("Did not receive prediction_update within 5 messages.")
    except Exception as e:
        print(f"WebSocket Error: {e}")

def main():
    print_header("1. Render Backend Validation")
    # Health Endpoint
    status, data = make_request("GET", f"{RENDER_URL}/health")
    print(f"[Health Endpoint] Status: {status}, Response: {data}")

    # Metrics Endpoint
    req = urllib.request.Request(f"{RENDER_URL}/metrics/prometheus", method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"[Metrics Endpoint] Status: {response.status}, Content Length: {len(response.read())} bytes")
    except urllib.error.HTTPError as e:
        print(f"[Metrics Endpoint] Failed: {e.code}")

    print_header("2. Vercel Frontend Validation")
    req = urllib.request.Request(VERCEL_URL, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode()
            print(f"[Vercel HTTP] Status: {response.status}")
            print(f"[Vercel Title] Contains 'NSE': {'NSE' in html or 'nse' in html.lower()}")
    except urllib.error.HTTPError as e:
        print(f"[Vercel HTTP] Failed: {e.code}")

    print_header("4. Internal Reload & Security Validation")
    # Missing token
    s1, d1 = make_request("POST", f"{RENDER_URL}/api/v1/internal/reload-models")
    print(f"[Reload Missing Token] Status: {s1}")
    
    # Invalid token
    s2, d2 = make_request("POST", f"{RENDER_URL}/api/v1/internal/reload-models", headers={"X-Internal-Token": "bad"})
    print(f"[Reload Invalid Token] Status: {s2}")
    
    # Valid token
    s3, d3 = make_request("POST", f"{RENDER_URL}/api/v1/internal/reload-models", headers={"X-Internal-Token": INTERNAL_TOKEN})
    print(f"[Reload Valid Token] Status: {s3}")
    if s3 in (200, 500):
        print(f"[Reload Response] {d3}")

    # Run websocket validation
    asyncio.run(validate_websocket())

if __name__ == "__main__":
    main()
