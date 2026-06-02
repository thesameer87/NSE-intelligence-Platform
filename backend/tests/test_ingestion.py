from unittest.mock import AsyncMock

import httpx
import pytest

from backend.config import Settings
from backend.ingestion.client import SmartAPIClient
from backend.ingestion.exceptions import SmartAPIError, IngestionValidationError
from backend.ingestion.schemas import NormalizedTick
from backend.ingestion.validator import normalize_ltp_payload


def test_payload_normalization() -> None:
    """Test valid payload normalizes correctly."""
    raw_payload = {
        "exchange": "NSE",
        "tradingsymbol": "RELIANCE-EQ",
        "symboltoken": "2885",
        "ltp": 2445.5,
        "volume": 1000,
    }

    tick = normalize_ltp_payload("RELIANCE", raw_payload)

    assert isinstance(tick, NormalizedTick)
    assert tick.symbol == "RELIANCE"
    assert tick.last_price == 2445.5
    assert tick.volume == 1000
    assert tick.timestamp is not None


def test_validation_behavior_missing_volume() -> None:
    """Test payload without volume safely defaults."""
    raw_payload = {"ltp": 2445.5}
    tick = normalize_ltp_payload("RELIANCE", raw_payload)
    assert tick.volume is None


def test_invalid_payload_rejection() -> None:
    """Test that malformed payloads raise ValidationError deterministically."""
    # Missing ltp completely
    with pytest.raises(
        IngestionValidationError, match="Failed to normalize LTP payload"
    ):
        normalize_ltp_payload("RELIANCE", {})

    # Invalid ltp type
    with pytest.raises(
        IngestionValidationError, match="Failed to normalize LTP payload"
    ):
        normalize_ltp_payload("RELIANCE", {"ltp": "INVALID"})


@pytest.fixture
def mock_settings() -> Settings:
    # Need to bypass pydantic validation for missing env vars
    # in tests if .env is missing
    # But settings might be fine. We just initialize it.
    return Settings(
        angel_one_api_key="mock_key",
        angel_one_client_id="mock_id",
        angel_one_password="mock_password",
        supabase_url="mock_url",
        supabase_key="mock_key",
        database_url="mock_db",
        jwt_secret="mock_jwt",
        internal_api_token="mock_internal",
    )


@pytest.mark.asyncio
async def test_mock_safe_ingestion_interface(mock_settings: Settings) -> None:
    """Test that the client cleanly handles a mocked httpx response."""

    # Create a mock response
    mock_response = httpx.Response(
        200,
        json={
            "status": True,
            "message": "SUCCESS",
            "errorcode": "",
            "data": {"ltp": 2500.0, "volume": 500},
        },
        request=httpx.Request(
            "POST",
            "https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/getLtpData",
        ),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.return_value = mock_response

    async with SmartAPIClient(settings=mock_settings, client=mock_client) as client:
        tick = await client.get_ltp("NSE", "RELIANCE", "2885")

        assert isinstance(tick, NormalizedTick)
        assert tick.last_price == 2500.0
        assert tick.volume == 500


@pytest.mark.asyncio
async def test_deterministic_failure_behavior(mock_settings: Settings) -> None:
    """Test that HTTP errors map perfectly to SmartAPIError."""

    # Create a mock error response
    mock_request = httpx.Request("POST", "https://mock")
    mock_response = httpx.Response(500, request=mock_request)

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # The client.post will return the response,
    # but response.raise_for_status() will throw
    mock_client.post.return_value = mock_response

    async with SmartAPIClient(settings=mock_settings, client=mock_client) as client:
        with pytest.raises(SmartAPIError, match="HTTP request failed"):
            await client.get_ltp("NSE", "RELIANCE", "2885")


@pytest.mark.asyncio
async def test_network_timeout_behavior(mock_settings: Settings) -> None:
    """Test that network timeouts raise SmartAPIError."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.post.side_effect = httpx.TimeoutException("Connection timed out")

    async with SmartAPIClient(settings=mock_settings, client=mock_client) as client:
        with pytest.raises(
            SmartAPIError, match="HTTP request failed: Connection timed out"
        ):
            await client.get_ltp("NSE", "RELIANCE", "2885")
