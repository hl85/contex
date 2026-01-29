import os
import json
from pathlib import Path
from dotenv import load_dotenv
from apps.sidecar.core.logger import get_logger

logger = get_logger("sidecar.config")

class ConfigManager:
    def __init__(self, config_filename: str = "config.json"):
        # Define configuration layers
        self.env_filename = ".env"
        self.config_filename = config_filename
        
        # Initialize paths
        self._init_paths()
        
        # Load configuration in layers
        self._config = {}
        self._env_vars = {}
        self._load_layers()
    
    def _init_paths(self):
        """Initialize configuration file paths with proper priority."""
        # Get project root (apps/sidecar/core/config.py -> ../../../)
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent
        
        # Priority order: CWD > Project Root
        cwd = Path(os.getcwd())
        
        # .env file paths
        self.env_paths = [
            cwd / self.env_filename,
            self.project_root / self.env_filename
        ]
        
        # config.json file paths  
        self.config_paths = [
            cwd / self.config_filename,
            self.project_root / self.config_filename
        ]
        
        # Find existing files
        self.env_file = None
        for path in self.env_paths:
            if path.exists():
                self.env_file = path
                break
                
        self.config_file = None
        for path in self.config_paths:
            if path.exists():
                self.config_file = path
                break
        
        logger.info(f"Config paths - .env: {self.env_file}, config.json: {self.config_file}")
    
    def _load_layers(self):
        """Load configuration in layers: L1(.env) -> L2(config.json)"""
        # Layer 1: Environment variables from .env file
        self._env_vars = {}
        if self.env_file:
            try:
                load_dotenv(self.env_file)
                # Load .env into internal storage for controlled access
                with open(self.env_file, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            self._env_vars[key] = value
                logger.info(f"Loaded environment variables from {self.env_file}")
            except Exception as e:
                logger.error(f"Failed to load .env file: {e}")
                self._env_vars = {}
        
        # Layer 2: Application config from config.json
        if self.config_file:
            try:
                with open(self.config_file, "r") as f:
                    self._config = json.load(f)
                logger.info(f"Loaded application config from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load config.json: {e}")
                self._config = {}
        else:
            logger.info("No config.json found. Using defaults.")
            self._config = {}

    def save(self, new_config: dict):
        """Save configuration to config.json, excluding sensitive keys."""
        try:
            # Use project root as default save location
            if not self.config_file:
                self.config_file = self.project_root / self.config_filename
                
            # Merge with existing, but exclude sensitive keys that should stay in .env
            sensitive_keys = {"GOOGLE_API_KEY", "DATABASE_URL", "SECRET_KEY"}
            for k, v in new_config.items():
                if k not in sensitive_keys:
                    self._config[k] = v
            
            # Ensure directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, "w") as f:
                json.dump(self._config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False

    def get(self, key: str, default=None):
        """Get configuration value with proper layer priority."""
        # Layer 1: .env file variables (highest priority for sensitive keys)
        if hasattr(self, '_env_vars') and key in self._env_vars:
            return self._env_vars[key]
            
        # Layer 2: Application config (config.json)
        if key in self._config:
            return self._config[key]
            
        # Layer 3: System environment variables (lowest priority, for non-sensitive keys)
        if key in os.environ and key not in ["GOOGLE_API_KEY", "DATABASE_URL", "SECRET_KEY"]:
            return os.environ[key]
            
        # Return default if not found
        return default
    
    def get_all(self):
        """Get all configuration excluding sensitive environment variables."""
        result = self._config.copy()
        
        # Add non-sensitive environment variables for transparency
        if hasattr(self, '_env_vars'):
            env_vars = {
                "DEBUG_MODE": self._env_vars.get("DEBUG_MODE"),
                "LOG_LEVEL": self._env_vars.get("LOG_LEVEL"),
                "PYTHONPATH": self._env_vars.get("PYTHONPATH")
            }
        else:
            env_vars = {
                "DEBUG_MODE": os.environ.get("DEBUG_MODE"),
                "LOG_LEVEL": os.environ.get("LOG_LEVEL"),
                "PYTHONPATH": os.environ.get("PYTHONPATH")
            }
        
        # Only include non-None values
        for k, v in env_vars.items():
            if v is not None:
                result[k] = v
                
        return result
    
    def get_sensitive_info(self):
        """Get sensitive configuration status for debugging."""
        api_key = None
        if hasattr(self, '_env_vars'):
            api_key = bool(self._env_vars.get("GOOGLE_API_KEY"))
        else:
            api_key = bool(os.environ.get("GOOGLE_API_KEY"))
            
        return {
            "env_file_exists": self.env_file is not None,
            "env_file_path": str(self.env_file) if self.env_file else None,
            "config_file_exists": self.config_file is not None, 
            "config_file_path": str(self.config_file) if self.config_file else None,
            "api_key_configured": api_key,
            "debug_mode": self.get("DEBUG_MODE", "False"),
            "log_level": self.get("LOG_LEVEL", "INFO")
        }

# Singleton instance
config_manager = ConfigManager()
