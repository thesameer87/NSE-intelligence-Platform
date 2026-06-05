import pytest
from httpx import AsyncClient, ASGITransport
import sentry_sdk
from unittest.mock import patch

from backend.main import app
from backend.config import Settings
from backend.utils.sentry import setup_sentry

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Verify the existing JSON metrics stub remains intact."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stub"
        assert "Metrics will be exposed here in V1" in data["message"]

@pytest.mark.asyncio
async def test_prometheus_endpoint():
    """Verify the new Prometheus text format metrics endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/metrics/prometheus")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        # Check that one of our custom metrics exists in the text output
        text = response.text
        assert "http_requests_total" in text
        assert "websocket_connections" in text
        assert "scheduler_iterations" in text

def test_sentry_disabled():
    """Verify app functions without initializing Sentry if DSN is missing."""
    settings = Settings(sentry_dsn=None) # type: ignore
    with patch("sentry_sdk.init") as mock_init:
        setup_sentry(settings)
        mock_init.assert_not_called()

def test_sentry_enabled():
    """Verify Sentry SDK initializes when DSN is provided, without network traffic."""
    settings = Settings(sentry_dsn="https://mock@sentry.io/123456") # type: ignore
    with patch("sentry_sdk.init") as mock_init:
        setup_sentry(settings)
        mock_init.assert_called_once()
        call_kwargs = mock_init.call_args.kwargs
        assert call_kwargs["dsn"] == "https://mock@sentry.io/123456"
        assert call_kwargs["environment"] == settings.environment
        assert "integrations" in call_kwargs
