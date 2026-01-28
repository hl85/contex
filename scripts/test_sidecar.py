import requests
import time
import subprocess
import sys
import os

def test_sidecar_health():
    # Start the sidecar in a separate process
    process = subprocess.Popen(
        [sys.executable, "apps/sidecar/api/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for server to start
        time.sleep(2)
        
        # Test Health
        try:
            resp = requests.get("http://127.0.0.1:12345/health")
            assert resp.status_code == 200
            assert resp.json()["status"] == "ok"
            print("✅ Health Check Passed")
        except Exception as e:
            print(f"❌ Health Check Failed: {e}")
            raise

        # Test Notification
        try:
            payload = {"title": "Test Brief", "content": "This is a test."}
            resp = requests.post("http://127.0.0.1:12345/notify", json=payload)
            assert resp.status_code == 200
            print("✅ Notification Endpoint Passed")
        except Exception as e:
            print(f"❌ Notification Endpoint Failed: {e}")
            raise
            
    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    test_sidecar_health()
