import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from backend.config import Settings
from backend.utils.logger import logger

def setup_sentry(settings: Settings) -> None:
    """Initialize Sentry for crash reporting if a DSN is provided."""
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not provided, Sentry will remain disabled.")
        return

    logger.info("Initializing Sentry SDK...")
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        integrations=[FastApiIntegration()],
        # Adjust traces_sample_rate depending on production traffic volume
        traces_sample_rate=1.0 if settings.environment != "production" else 0.1,
    )
