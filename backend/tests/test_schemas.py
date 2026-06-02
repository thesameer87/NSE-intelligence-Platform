from datetime import date, datetime, timezone
import uuid

import pytest
from pydantic import ValidationError

from backend.schemas.common import TimeStampedSchema
from backend.schemas.health import HealthResponse
from backend.schemas.market import IntradayTickCreate, DailyOHLCVCreate
from backend.schemas.prediction import PredictionResponse, IntradayPrediction, NextDayPrediction, Corridor
from backend.schemas.signal import TradingSignalCreate
from backend.schemas.portfolio import PortfolioHoldingCreate


def test_timestamped_schema() -> None:
    """Test that timestamped schema properly serializes datetime fields."""
    now = datetime.now(timezone.utc)
    schema = TimeStampedSchema(created_at=now)
    assert schema.created_at == now
    assert schema.updated_at is None

    # Should serialize properly to dict
    data = schema.model_dump()
    assert "created_at" in data
    assert "updated_at" in data


def test_health_response() -> None:
    """Test health response schema."""
    health = HealthResponse(status="ok", service="backend", environment="development")
    assert health.status == "ok"


def test_invalid_confidence_rejection() -> None:
    """Test that confidence fields enforce ge=0.0, le=1.0 constraints."""
    
    # IntradayPrediction should reject confidence > 1.0
    with pytest.raises(ValidationError) as exc_info:
        IntradayPrediction(direction="Bullish", confidence=1.5, target_price=2800)
    assert "Input should be less than or equal to 1" in str(exc_info.value)
    
    # IntradayPrediction should reject confidence < 0.0
    with pytest.raises(ValidationError) as exc_info:
        IntradayPrediction(direction="Bullish", confidence=-0.5, target_price=2800)
    assert "Input should be greater than or equal to 0" in str(exc_info.value)
    
    # Valid confidence should pass
    valid = IntradayPrediction(direction="Bullish", confidence=0.85, target_price=2800)
    assert valid.confidence == 0.85


def test_prediction_response() -> None:
    """Test nested prediction response structure."""
    intraday = IntradayPrediction(direction="Bullish", confidence=0.82, target_price=2870.0)
    nextday = NextDayPrediction(
        direction="Bullish", 
        confidence=0.79, 
        corridor=Corridor(lower=2860.0, upper=2915.0)
    )
    
    pred = PredictionResponse(
        symbol="RELIANCE",
        intraday=intraday,
        nextday=nextday
    )
    
    dumped = pred.model_dump()
    assert dumped["symbol"] == "RELIANCE"
    assert dumped["intraday"]["target_price"] == 2870.0
    assert dumped["nextday"]["corridor"]["upper"] == 2915.0


def test_market_tick_defaults() -> None:
    """Test that market tick defaults are set appropriately."""
    tick = IntradayTickCreate(
        symbol="HDFC",
        timestamp=datetime.now(timezone.utc),
        ltp=1500.0,
        bid_price=1499.5,
        ask_price=1500.5,
        bid_qty=100,
        ask_qty=100,
        volume=50000
    )
    # Default should be False
    assert tick.cold_storage_uploaded is False


def test_portfolio_holding_optional() -> None:
    """Test that portfolio holding notes are correctly optional."""
    holding = PortfolioHoldingCreate(
        symbol="RELIANCE",
        quantity=50.5,
        avg_buy_price=2500.0,
        buy_date=date.today()
        # notes omitted
    )
    assert holding.notes is None


def test_missing_required_fields() -> None:
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        HealthResponse(status="ok", service="backend") # type: ignore
    assert "environment" in str(exc_info.value)
    assert "Field required" in str(exc_info.value)


def test_invalid_types() -> None:
    """Test that invalid types raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        IntradayPrediction(direction="Bullish", confidence="HIGH", target_price=2800.0) # type: ignore
    assert "confidence" in str(exc_info.value)
    assert "Input should be a valid number" in str(exc_info.value)


def test_json_serialization() -> None:
    """Test model_dump_json serialization."""
    health = HealthResponse(status="ok", service="backend", environment="dev")
    json_str = health.model_dump_json()
    assert '"status":"ok"' in json_str
    assert '"environment":"dev"' in json_str


def test_orm_serialization() -> None:
    """Test ORM serialization via from_attributes=True."""
    class MockORM:
        def __init__(self, status: str, service: str, environment: str) -> None:
            self.status = status
            self.service = service
            self.environment = environment
            
    mock_db_obj = MockORM(status="ok", service="api", environment="prod")
    health = HealthResponse.model_validate(mock_db_obj)
    assert health.status == "ok"
    assert health.environment == "prod"
