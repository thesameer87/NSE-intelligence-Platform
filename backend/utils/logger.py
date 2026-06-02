import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict

from backend.config import Settings

# Instantiate locally to fail-fast if environment is missing before logger mounts
settings_for_log = Settings()  # type: ignore[call-arg]

class JSONFormatter(logging.Formatter):
    """
    Production-grade JSON formatter for all application logs.
    Ensures logs are ingestible by centralized logging systems.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "service": "nse-intelligence-platform",
            "message": record.getMessage(),
            "correlation_id": getattr(record, "correlation_id", None),
            "environment": settings_for_log.environment,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("nse_platform")
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        
        # Production uses INFO to reduce noise; lower environments use DEBUG
        if settings_for_log.environment == "production":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)
            
        logger.propagate = False

    return logger

logger = setup_logger()
