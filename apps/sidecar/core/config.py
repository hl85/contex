import os
import json
from pathlib import Path
from apps.sidecar.core.logger import get_logger

logger = get_logger("sidecar.config")

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        # Use a path relative to the sidecar execution or a fixed user home path
        # For MVP, we'll try to put it in the project root or current working dir
        self.config_path = Path(os.getcwd()) / config_path
        self._config = {}
        self._load()

    def _load(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r") as f:
                    self._config = json.load(f)
                logger.info(f"Loaded config from {self.config_path}")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._config = {}
        else:
            logger.info("No config file found. Using defaults.")
            self._config = {}

    def save(self, new_config: dict):
        try:
            # Merge with existing
            self._config.update(new_config)
            with open(self.config_path, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info("Configuration saved.")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default=None):
        return self._config.get(key, default)

    def get_all(self):
        return self._config.copy()

# Singleton instance
config_manager = ConfigManager()
