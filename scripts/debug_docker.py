import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()
print(f"USE_MOCK_DOCKER from env: {os.getenv('USE_MOCK_DOCKER')}")

try:
    import docker
    print("Docker SDK imported successfully.")
    try:
        client = docker.from_env()
        print("docker.from_env() called.")
        client.ping()
        print("Docker daemon ping successful!")
    except Exception as e:
        print(f"Docker connection failed: {e}")
except ImportError:
    print("Docker SDK not installed.")
