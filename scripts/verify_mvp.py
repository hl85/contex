import requests
import time
import subprocess
import sys
import threading
import signal
import os

SIDECAR_URL = "http://127.0.0.1:12345"

def stream_logs(process, success_event):
    """
    Reads stdout from the sidecar process and checks for the success signal.
    """
    for line in iter(process.stdout.readline, ''):
        print(f"[Sidecar Log] {line.strip()}")
        if "[NOTIFICATION] Title: Daily News Brief" in line:
            print("✅ SUCCESS: Notification received from Sidecar!")
            success_event.set()

def verify_integration():
    print("=== Starting MVP Verification ===")
    
    # Start Sidecar
    print("[*] Launching Sidecar...")
    process = subprocess.Popen(
        [sys.executable, "apps/sidecar/api/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # Merge stderr into stdout
        text=True,
        bufsize=1,
        env=os.environ.copy() # Ensure it has path to modules
    )
    
    success_event = threading.Event()
    log_thread = threading.Thread(target=stream_logs, args=(process, success_event))
    log_thread.daemon = True
    log_thread.start()
    
    try:
        # Wait for health check
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

        # Trigger Task
        print("[*] Triggering Daily Brief Task...")
        try:
            resp = requests.post(f"{SIDECAR_URL}/run-task", json={"task_name": "daily-brief"})
            resp.raise_for_status()
            print("[*] Task triggered successfully.")
        except Exception as e:
            print(f"❌ Failed to trigger task: {e}")
            return

        # Wait for notification
        print("[*] Waiting for callback notification...")
        if success_event.wait(timeout=30):  # Increased timeout for LLM/Search latency
            print("🎉 MVP Verification PASSED!")
        else:
            print("❌ Timeout waiting for notification.")
            
    finally:
        print("[*] Cleaning up...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    verify_integration()
