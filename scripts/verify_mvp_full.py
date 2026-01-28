import requests
import time
import subprocess
import sys
import threading
import os
import json

SIDECAR_URL = "http://127.0.0.1:12345"
TEST_API_KEY = "TEST_KEY_VERIFICATION_123"

def stream_logs(process, success_event, failure_event):
    """
    Reads stdout from the sidecar process.
    """
    for line in iter(process.stdout.readline, ''):
        print(f"[Sidecar Log] {line.strip()}")
        
        # Check for Key Warning (We want to ensure this DOES NOT happen if we set the key)
        if "GOOGLE_API_KEY not found" in line:
            print("❌ FAILURE: Skill reported missing API Key despite config!")
            failure_event.set()

        # Check for success notification
        if "[NOTIFICATION] Title: Daily News Brief" in line:
            print("✅ SUCCESS: Notification received from Sidecar!")
            success_event.set()

def verify_full_mvp():
    print("=== Starting Full MVP Verification (Config + Execution) ===")
    
    # 1. Start Sidecar
    print("[*] Launching Sidecar...")
    env = os.environ.copy()
    # Ensure PYTHONPATH includes project root
    env["PYTHONPATH"] = os.getcwd()
    
    process = subprocess.Popen(
        [sys.executable, "apps/sidecar/api/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        env=env
    )
    
    success_event = threading.Event()
    failure_event = threading.Event()
    
    log_thread = threading.Thread(target=stream_logs, args=(process, success_event, failure_event))
    log_thread.daemon = True
    log_thread.start()
    
    try:
        # 2. Wait for Health Check
        print("[*] Waiting for Sidecar to be healthy...")
        for _ in range(10):
            try:
                requests.get(f"{SIDECAR_URL}/health")
                print("[*] Sidecar is healthy.")
                break
            except:
                time.sleep(1)
        else:
            print("❌ Sidecar failed to start.")
            return

        # 3. Configure API Key
        print(f"[*] Setting Configuration with Key: {TEST_API_KEY}...")
        try:
            resp = requests.post(f"{SIDECAR_URL}/config", json={"config": {"GOOGLE_API_KEY": TEST_API_KEY}})
            resp.raise_for_status()
            print("[*] Configuration saved.")
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return

        # 4. Verify Persistence (Check file)
        if os.path.exists("config.json"):
            with open("config.json") as f:
                data = json.load(f)
                if data.get("GOOGLE_API_KEY") == TEST_API_KEY:
                    print("[*] Verified config.json persistence ✅")
                else:
                    print("❌ config.json content mismatch!")
        else:
            print("❌ config.json not created!")

        # 5. Trigger Task
        print("[*] Triggering Daily Brief Task...")
        try:
            resp = requests.post(f"{SIDECAR_URL}/run-task", json={"task_name": "daily-brief"})
            resp.raise_for_status()
            print("[*] Task triggered successfully.")
        except Exception as e:
            print(f"❌ Failed to trigger task: {e}")
            return

        # 6. Wait for Completion
        print("[*] Waiting for task completion...")
        # We give it some time. If failure_event is set, we fail early.
        start_time = time.time()
        while time.time() - start_time < 30:
            if failure_event.is_set():
                print("❌ Verification Failed: Logic Error Detected.")
                return
            if success_event.is_set():
                print("🎉 Full MVP Verification PASSED!")
                return
            time.sleep(0.5)
        
        print("❌ Timeout waiting for notification.")
            
    finally:
        print("[*] Cleaning up...")
        process.terminate()
        process.wait()
        # Clean up config file to reset state
        if os.path.exists("config.json"):
            os.remove("config.json")

if __name__ == "__main__":
    verify_full_mvp()
