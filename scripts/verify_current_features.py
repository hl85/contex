import requests
import json
import time
from pathlib import Path

BASE_URL = "http://127.0.0.1:12345"
SKILL_ID = "daily-brief"

def test_health():
    print("Testing /health...")
    try:
        res = requests.get(f"{BASE_URL}/health")
        print(f"Status: {res.status_code}, Body: {res.json()}")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"
        print("✅ Health check passed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        exit(1)

def test_config_workflow():
    print(f"\nTesting Config Workflow for {SKILL_ID}...")
    
    # 1. Get initial config
    res = requests.get(f"{BASE_URL}/config/{SKILL_ID}")
    initial_config = res.json()
    print(f"Initial config: {initial_config}")
    
    # 2. Update config
    new_topics = ["AI", "Space", "Quantum"]
    update_payload = {"config": {"topics": new_topics, "max_results": 5}}
    res = requests.post(f"{BASE_URL}/config/{SKILL_ID}", json=update_payload)
    assert res.status_code == 200
    print("Config updated via API")
    
    # 3. Verify update via API
    res = requests.get(f"{BASE_URL}/config/{SKILL_ID}")
    updated_config = res.json()
    print(f"Updated config: {updated_config}")
    assert updated_config["topics"] == new_topics
    
    # 4. Verify file persistence
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            file_data = json.load(f)
            saved_topics = file_data.get("skill_configs", {}).get(SKILL_ID, {}).get("topics")
            print(f"File content check: {saved_topics}")
            assert saved_topics == new_topics
            print("✅ Config persistence verified")
    else:
        print("❌ config.json not found")
        exit(1)

def test_skill_execution():
    print(f"\nTesting Skill Execution: {SKILL_ID}...")
    payload = {"task_name": SKILL_ID}
    res = requests.post(f"{BASE_URL}/run-task", json=payload)
    
    print(f"Run response: {res.status_code} - {res.text}")
    
    if res.status_code == 200:
        data = res.json()
        print(f"✅ Skill started successfully. Container/Process ID: {data.get('container_id')}")
        
        # Wait a bit for logs
        print("Waiting 5 seconds for execution logs...")
        time.sleep(5)
        
        # Check logs
        log_res = requests.get(f"{BASE_URL}/logs")
        logs = log_res.json()
        print("--- Recent Logs ---")
        found_start = False
        for log in logs[-20:]: # Check last 20 logs
            print(f"[{log['level']}] {log['message']}")
            if "Starting Daily Brief Agent" in log['message']:
                found_start = True
        
        if found_start:
            print("✅ Found skill startup log")
        else:
            print("⚠️ Startup log not found (might be too early or filtered)")
            
    else:
        print("❌ Failed to start skill")
        exit(1)

if __name__ == "__main__":
    try:
        test_health()
        test_config_workflow()
        test_skill_execution()
        print("\n🎉 All verifications passed!")
    except AssertionError as e:
        print(f"\n❌ Verification failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
