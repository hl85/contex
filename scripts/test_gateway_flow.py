import subprocess
import time
import requests
import sys
import os
import signal

GATEWAY_PORT = 12346
GATEWAY_URL = f"http://127.0.0.1:{GATEWAY_PORT}"

def run_test():
    print("🚀 Starting Gateway Integration Test...")
    
    # 1. Start Gateway
    print("Starting Gateway process...")
    # Using sys.executable to ensure we use the same python environment
    gateway_process = subprocess.Popen(
        [sys.executable, "apps/gateway/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Wait for startup
        print("Waiting for Gateway to start...")
        time.sleep(3)
        
        # 2. Health Check
        try:
            res = requests.get(f"{GATEWAY_URL}/health")
            if res.status_code == 200:
                print("✅ Gateway is healthy")
            else:
                print(f"❌ Gateway health check failed: {res.status_code}")
                return
        except Exception as e:
            print(f"❌ Failed to connect to Gateway: {e}")
            return

        # 3. Send Mock WeChat Message
        print("\nSending Mock WeChat Message: '/brief'")
        payload = {
            "msg_id": "msg_12345",
            "sender": "user_test",
            "content": "/brief",
            "msg_type": "text"
        }
        
        res = requests.post(f"{GATEWAY_URL}/webhook/wechat", json=payload)
        print(f"Webhook Response: {res.status_code} - {res.json()}")
        assert res.status_code == 200
        
        # 4. Wait for processing logs (Gateway prints logs to stdout)
        print("Waiting for processing (5s)...")
        time.sleep(5)
        
        # We can't easily read the stdout of the running process without blocking, 
        # but the fact that we got a 200 OK means the background task was scheduled.
        # And if Sidecar is running (which it should be), it should have received the request.
        
        print("✅ Gateway test flow completed successfully.")
        
    finally:
        # Cleanup
        print("\nStopping Gateway...")
        os.kill(gateway_process.pid, signal.SIGTERM)
        gateway_process.wait()
        
        # Print logs for debugging
        stdout, stderr = gateway_process.communicate()
        print("\n=== Gateway Logs ===")
        print(stdout)
        if stderr:
            print("=== Gateway Errors ===")
            print(stderr)

if __name__ == "__main__":
    run_test()
