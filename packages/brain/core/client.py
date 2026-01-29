import requests
from google import genai
from .config import config
from .logger import setup_logger

logger = setup_logger("brain.core.client")

class SidecarClient:
    def __init__(self):
        self.base_url = config.get("SIDECAR_URL", "http://host.docker.internal:12345")

    def notify(self, title: str, content: str):
        """Send notification/result to Sidecar."""
        try:
            url = f"{self.base_url}/notify"
            payload = {"title": title, "content": content}
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            logger.info(f"Notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

class AIClientFactory:
    @staticmethod
    def get_client():
        """Initialize Google GenAI Client."""
        api_key = config.require("GOOGLE_API_KEY")
        return genai.Client(api_key=api_key)

# Singleton instances
sidecar = SidecarClient()
