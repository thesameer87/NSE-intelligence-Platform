import logging
from typing import Any
from backend.config import Settings

logger = logging.getLogger(__name__)

def validate_configuration(**kwargs: Any) -> Settings:
    """
    Validates the configuration at startup.
    Pydantic will automatically raise ValidationError if required fields are missing.
    This function performs additional semantic checks if needed.
    """
    try:
        settings = Settings(**kwargs)
        if settings.environment == "production" and settings.scheduler_interval_seconds < 30:
            logger.warning("Production environment detected but scheduler_interval_seconds is less than 30.")
        
        logger.info(f"Configuration validated successfully for environment: {settings.environment}")
        return settings
    except Exception as e:
        logger.critical(f"Configuration validation failed: {e}")
        raise
