import uuid
from typing import AsyncGenerator
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from backend.db.dependencies import get_db_session
from backend.db.models.market_tick import DailyOHLCV, IntradayTick
from backend.db.models.portfolio import PortfolioHolding
from backend.db.models.prediction import ModelRegistry
from backend.db.models.signal import TradingSignal
from backend.main import app

# Create a global mock session for tests
mock_db_session = AsyncMock()


async def override_get_db_session() -> AsyncGenerator[AsyncMock, None]:
    yield mock_db_session


app.dependency_overrides[get_db_session] = override_get_db_session

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock_session() -> None:
    """Reset the mock session before each test."""
    mock_db_session.reset_mock()
    mock_db_session.execute.side_effect = None
    # By default, mock_db_session.execute returns a MagicMock() 
    # so we can chain .scalars().all()
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = []
    mock_db_session.execute.return_value = mock_result


def test_get_intraday_ticks_success() -> None:
    """Test reading intraday ticks successfully."""
    mock_tick = IntradayTick(
        id=uuid.uuid4(),
        symbol="RELIANCE",
        timestamp=datetime.now(timezone.utc),
        ltp=2500.0,
        volume=1000,
        cold_storage_uploaded=False,
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_tick]
    mock_db_session.execute.return_value = mock_result

    response = client.get("/api/v1/market/ticks/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "RELIANCE"
    assert data[0]["ltp"] == 2500.0


def test_get_intraday_ticks_db_error() -> None:
    """Test DB failure mapping."""
    mock_db_session.execute.side_effect = OperationalError(
        "connection dropped", params={}, orig=Exception()
    )

    response = client.get("/api/v1/market/ticks/RELIANCE")
    assert response.status_code == 500
    assert response.json()["detail"] == "Database operation failed"


def test_get_daily_ohlcv_success() -> None:
    """Test reading daily OHLCV successfully."""
    mock_bar = DailyOHLCV(
        id=uuid.uuid4(),
        symbol="RELIANCE",
        trade_date=datetime.now(timezone.utc).date(),
        open=2400.0,
        high=2500.0,
        low=2350.0,
        close=2450.0,
        volume=50000,
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_bar]
    mock_db_session.execute.return_value = mock_result

    response = client.get("/api/v1/market/ohlcv/RELIANCE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "RELIANCE"


def test_get_latest_models_success() -> None:
    """Test reading latest models successfully."""
    mock_model = ModelRegistry(
        model_name="xgboost_intraday",
        version="v1.0.0",
        trained_at=datetime.now(timezone.utc),
        metrics_json={"accuracy": 0.85},
        schema_version="1.0",
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_model]
    mock_db_session.execute.return_value = mock_result

    response = client.get("/api/v1/prediction/models/latest")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["model_name"] == "xgboost_intraday"


def test_get_prediction_not_found() -> None:
    """Test prediction endpoint returns 404 (not yet implemented in DB)."""
    response = client.get("/api/v1/prediction/RELIANCE")
    assert response.status_code == 404
    assert response.json()["detail"] == "No prediction data found for RELIANCE"


def test_get_signals_success() -> None:
    """Test reading signals successfully."""
    mock_signal = TradingSignal(
        id=uuid.uuid4(),
        symbol="RELIANCE",
        signal="Bullish",
        confidence=0.8,
        target_price=2600.0,
        prediction_source="xgboost_intraday",
        created_at=datetime.now(timezone.utc),
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_signal]
    mock_db_session.execute.return_value = mock_result

    response = client.get("/api/v1/signal/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "RELIANCE"
    assert data[0]["signal"] == "Bullish"


def test_get_portfolio_holdings_success() -> None:
    """Test reading portfolio holdings successfully."""
    mock_holding = PortfolioHolding(
        symbol="RELIANCE",
        quantity=50.0,
        avg_buy_price=2400.0,
        buy_date=datetime.now(timezone.utc).date(),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_holding]
    mock_db_session.execute.return_value = mock_result

    response = client.get("/api/v1/portfolio/holdings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == "RELIANCE"
    assert data[0]["quantity"] == 50.0
