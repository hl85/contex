import os
import json
from pathlib import Path
from apps.sidecar.core.logger import get_logger

logger = get_logger("sidecar.config")

class ConfigManager:
    def __init__(self, config_filename: str = "config.json"):
        # Try current working directory first
        cwd_path = Path(os.getcwd()) / config_filename
        
        # Try project root (relative to this file: apps/sidecar/core/config.py -> ../../../config.json)
        # This assumes the file is in apps/sidecar/core/config.py
        # Path(__file__) is absolute path of config.py
        # .parent (core) -> .parent (sidecar) -> .parent (apps) -> .parent (root)
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        root_path = project_root / config_filename
        
        if cwd_path.exists():
            self.config_path = cwd_path
        elif root_path.exists():
            self.config_path = root_path
        else:
            # Default to CWD if neither exists
            self.config_path = cwd_path
            
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
