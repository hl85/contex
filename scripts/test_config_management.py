#!/usr/bin/env python3
"""
Configuration Management Test Script
Tests the layered configuration loading mechanism
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

from apps.sidecar.core.config import ConfigManager
from apps.sidecar.core.logger import get_logger

logger = get_logger("config.test")

def test_config_layers():
    """Test configuration layer loading and priority."""
    print("=== Testing Configuration Layer Management ===")
    
    # Create temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create test .env file
        env_file = temp_path / ".env"
        env_file.write_text("GOOGLE_API_KEY=env_test_key\nDEBUG_MODE=true\nLOG_LEVEL=DEBUG\n")
        
        # Create test config.json file
        config_file = temp_path / "config.json"
        config_data = {
            "DEBUG_MODE": "false",
            "LOG_LEVEL": "INFO", 
            "skill_configs": {
                "daily-brief": {
                    "topics": ["Test Topic"],
                    "max_results": 5
                }
            }
        }
        config_file.write_text(json.dumps(config_data, indent=2))
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Initialize config manager
            config_mgr = ConfigManager()
            
            print(f"✅ Config manager initialized")
            print(f"   - .env file: {config_mgr.env_file}")
            print(f"   - config.json file: {config_mgr.config_file}")
            
            # Test layer priority
            print("\n--- Testing Layer Priority ---")
            
            # GOOGLE_API_KEY should come from .env (L1)
            api_key = config_mgr.get("GOOGLE_API_KEY")
            print(f"GOOGLE_API_KEY: {api_key} (should be 'env_test_key')")
            assert api_key == "env_test_key", f"Expected 'env_test_key', got '{api_key}'"
            
            # DEBUG_MODE should prioritize system env > .env > config.json
            debug_mode = config_mgr.get("DEBUG_MODE")
            print(f"DEBUG_MODE: {debug_mode} (should be 'true' from .env)")
            assert debug_mode == "true", f"Expected 'true', got '{debug_mode}'"
            
            # LOG_LEVEL should prioritize .env over config.json
            log_level = config_mgr.get("LOG_LEVEL")
            print(f"LOG_LEVEL: {log_level} (should be 'DEBUG' from .env)")
            assert log_level == "DEBUG", f"Expected 'DEBUG', got '{log_level}'"
            
            # skill_configs should come from config.json
            skill_configs = config_mgr.get("skill_configs")
            print(f"skill_configs: {skill_configs}")
            assert skill_configs == config_data["skill_configs"]
            
            print("✅ Layer priority test passed")
            
            # Test save functionality
            print("\n--- Testing Save Functionality ---")
            
            new_config = {
                "NEW_SETTING": "test_value",
                "skill_configs": {
                    "daily-brief": {
                        "topics": ["Updated Topic"],
                        "max_results": 10
                    }
                }
            }
            
            success = config_mgr.save(new_config)
            assert success, "Save should succeed"
            
            # Verify save excluded sensitive keys
            with open(config_mgr.config_file, "r") as f:
                saved_data = json.load(f)
            
            assert "GOOGLE_API_KEY" not in saved_data, "API key should not be saved to config.json"
            assert saved_data["NEW_SETTING"] == "test_value", "New setting should be saved"
            
            print("✅ Save functionality test passed")
            
            # Test get_all method
            print("\n--- Testing get_all Method ---")
            
            all_config = config_mgr.get_all()
            print(f"All config keys: {list(all_config.keys())}")
            
            # Should include non-sensitive env vars
            assert "DEBUG_MODE" in all_config
            assert "LOG_LEVEL" in all_config
            # Should not include sensitive env vars
            assert "GOOGLE_API_KEY" not in all_config
            
            print("✅ get_all method test passed")
            
            # Test sensitive info method
            print("\n--- Testing Sensitive Info Method ---")
            
            sensitive_info = config_mgr.get_sensitive_info()
            print(f"Sensitive info: {sensitive_info}")
            
            assert sensitive_info["api_key_configured"] == True
            assert sensitive_info["env_file_exists"] == True
            assert sensitive_info["config_file_exists"] == True
            
            print("✅ Sensitive info test passed")
            
            print("\n🎉 All configuration management tests passed!")
            return True
            
        finally:
            os.chdir(original_cwd)

def test_config_with_system_env():
    """Test configuration with system environment variables."""
    print("\n=== Testing System Environment Override ===")
    
    # Set system environment variable (non-sensitive key)
    original_pythonpath = os.environ.get("PYTHONPATH")
    os.environ["PYTHONPATH"] = "system_override_path"
    
    try:
        config_mgr = ConfigManager()
        
        # System env should override for non-sensitive keys (when not in .env)
        pythonpath = config_mgr.get("PYTHONPATH")
        print(f"PYTHONPATH with system override: {pythonpath}")
        assert pythonpath == "system_override_path", f"Expected 'system_override_path', got '{pythonpath}'"
        
        # But .env should still override system env for keys present in .env
        debug_mode = config_mgr.get("DEBUG_MODE")  # This should still come from .env if present
        print(f"DEBUG_MODE (should not be overridden by system): {debug_mode}")
        
        print("✅ System environment override test passed")
        
    finally:
        # Restore original value
        if original_pythonpath is not None:
            os.environ["PYTHONPATH"] = original_pythonpath
        elif "PYTHONPATH" in os.environ:
            del os.environ["PYTHONPATH"]

if __name__ == "__main__":
    try:
        test_config_layers()
        test_config_with_system_env()
        print("\n🎉 All configuration tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        sys.exit(1)