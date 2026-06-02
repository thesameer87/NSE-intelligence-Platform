from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from backend.db.models.market_tick import IntradayTick
from backend.ingestion.schemas import NormalizedTick
from backend.persistence.exceptions import DatabaseOperationError
from backend.persistence.market import MarketDataRepository


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def sample_tick() -> NormalizedTick:
    return NormalizedTick(
        symbol="RELIANCE",
        timestamp=datetime.now(timezone.utc),
        last_price=2500.5,
        volume=1000,
    )


@pytest.mark.asyncio
async def test_save_tick_success(
    mock_session: AsyncMock, sample_tick: NormalizedTick
) -> None:
    """Test successful persistence of a NormalizedTick to IntradayTick."""
    repo = MarketDataRepository(session=mock_session)
    await repo.save_tick(sample_tick)

    # Verify model translation
    mock_session.add.assert_called_once()
    added_instance = mock_session.add.call_args[0][0]

    assert isinstance(added_instance, IntradayTick)
    assert added_instance.symbol == "RELIANCE"
    assert added_instance.ltp == 2500.5
    assert added_instance.volume == 1000
    # Missing L2 data should be explicitly None
    assert added_instance.bid_price is None

    # Verify commit happened
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_save_tick_db_error(
    mock_session: AsyncMock, sample_tick: NormalizedTick
) -> None:
    """Test deterministic mapping of DB errors during save, and rollback behavior."""
    # Simulate DB commit failure
    mock_session.commit.side_effect = OperationalError(
        "connection dropped", params={}, orig=Exception()
    )

    repo = MarketDataRepository(session=mock_session)

    with pytest.raises(
        DatabaseOperationError, match="Database error while saving tick"
    ):
        await repo.save_tick(sample_tick)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_latest_tick_found(mock_session: AsyncMock) -> None:
    """Test retrieving and translating an IntradayTick back to NormalizedTick."""
    mock_result = MagicMock()
    mock_db_tick = IntradayTick(
        symbol="HDFC", timestamp=datetime.now(timezone.utc), ltp=1600.0, volume=500
    )
    mock_result.scalar_one_or_none.return_value = mock_db_tick
    mock_session.execute.return_value = mock_result

    repo = MarketDataRepository(session=mock_session)
    tick = await repo.get_latest_tick("HDFC")

    assert isinstance(tick, NormalizedTick)
    assert tick.symbol == "HDFC"
    assert tick.last_price == 1600.0
    assert tick.volume == 500


@pytest.mark.asyncio
async def test_get_latest_tick_not_found(mock_session: AsyncMock) -> None:
    """Test returning None when no records exist."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    repo = MarketDataRepository(session=mock_session)
    tick = await repo.get_latest_tick("UNKNOWN")

    assert tick is None


@pytest.mark.asyncio
async def test_get_latest_tick_db_error(mock_session: AsyncMock) -> None:
    """Test DB failure mapping during read operations."""
    mock_session.execute.side_effect = OperationalError(
        "connection dropped", params={}, orig=Exception()
    )

    repo = MarketDataRepository(session=mock_session)

    with pytest.raises(
        DatabaseOperationError, match="Database error while fetching tick"
    ):
        await repo.get_latest_tick("HDFC")
