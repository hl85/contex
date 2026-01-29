import os
import json
from typing import Any, Dict, Optional
from .logger import setup_logger

logger = setup_logger("brain.core.config")

class ConfigLoader:
    def __init__(self):
        self._config: Dict[str, Any] = {}
        self._load_from_env()

    def _load_from_env(self):
        # 1. Load global env vars
        self._config.update(os.environ)

        # 2. Load injected Skill Config (JSON)
        skill_config_str = os.environ.get("SKILL_CONFIG")
        if skill_config_str:
            try:
                skill_config = json.loads(skill_config_str)
                if isinstance(skill_config, dict):
                    self._config.update(skill_config)
                logger.info("Loaded SKILL_CONFIG successfully")
            except json.JSONDecodeError:
                logger.error("Failed to parse SKILL_CONFIG JSON")

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    def require(self, key: str) -> Any:
        val = self.get(key)
        if val is None:
            raise ValueError(f"Missing required configuration: {key}")
        return val

# Singleton instance
config = ConfigLoader()
