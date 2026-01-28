import logging
import json
import sys
from datetime import datetime
from collections import deque

# Global log buffer
LOG_BUFFER = deque(maxlen=1000)

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

def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        formatter = JsonFormatter()
        
        # Stdout handler
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)
        
        # Buffer handler
        buffer_handler = BufferHandler()
        buffer_handler.setFormatter(formatter)
        logger.addHandler(buffer_handler)
        
        logger.setLevel(logging.INFO)
    return logger

def get_logs(limit: int = 100):
    return list(LOG_BUFFER)[-limit:]
