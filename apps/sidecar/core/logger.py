import logging
import json
import sys
import os
from datetime import datetime
from collections import deque
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Global log buffer for real-time UI updates
LOG_BUFFER = deque(maxlen=1000)

# Define Log Directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "system.log"

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "task_id"):
            log_record["task_id"] = record.task_id
        return json.dumps(log_record)

class BufferHandler(logging.Handler):
    def emit(self, record):
        try:
            msg = self.format(record)
            LOG_BUFFER.append(json.loads(msg))
        except Exception:
            self.handleError(record)

def setup_logging_config():
    """
    Setup the root logger to write to file and stdout.
    This should be called once by the main application entry point.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    formatter = JsonFormatter()
    
    # 1. File Handler (Rotating)
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=10*1024*1024, backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # 2. Stdout Handler
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(formatter)
    root_logger.addHandler(stdout_handler)
    
    # 3. Buffer Handler (for UI API)
    buffer_handler = BufferHandler()
    buffer_handler.setFormatter(formatter)
    root_logger.addHandler(buffer_handler)

def get_logger(name: str):
    # Just return the logger, assuming setup_logging_config is called globally
    # or rely on root logger propagation
    logger = logging.getLogger(name)
    # Prevent adding handlers multiple times if get_logger is called repeatedly without setup
    # But for simplicity in this project, we'll ensure setup_logging_config is called in main.
    return logger

def get_logs(limit: int = 100):
    """
    Read the last N lines from the log file to ensure we capture logs from all processes 
    (Sidecar, Gateway, etc.) that write to the shared system.log.
    """
    logs = []
    if not LOG_FILE.exists():
        return []
        
    try:
        # Simple implementation using deque for tailing
        # For very large files, this might need optimization (seek to end and read backwards)
        # But given log rotation (10MB), reading the file is acceptable for MVP
        with open(LOG_FILE, 'r') as f:
            # Read all lines is expensive, so let's use a more efficient way for last N lines
            # Using deque with maxlen is memory efficient
            last_lines = deque(f, maxlen=limit)
            
            for line in last_lines:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    # Handle cases where line might not be valid JSON (e.g. stack traces)
                    logs.append({
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "level": "ERROR",
                        "component": "system",
                        "message": line.strip()
                    })
    except Exception as e:
        # Fallback to internal buffer if file read fails
        return list(LOG_BUFFER)[-limit:]
        
    return logs

def clear_logs():
    LOG_BUFFER.clear()
    # Optionally clear file? No, keep history in file.
