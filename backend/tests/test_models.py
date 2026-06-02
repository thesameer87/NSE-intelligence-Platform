import pytest
import os
import subprocess
import sys
from sqlalchemy import MetaData
from backend.db.base import Base
from backend.db.models import IntradayTick, DailyOHLCV, PortfolioHolding, TradingSignal, ModelRegistry

def test_model_imports_and_metadata() -> None:
    """Verify models are registered correctly with the Base metadata."""
    metadata: MetaData = Base.metadata
    
    assert "intraday_ticks" in metadata.tables
    assert "daily_ohlcv" in metadata.tables
    assert "portfolio_holdings" in metadata.tables
    assert "trading_signals" in metadata.tables
    assert "model_registry" in metadata.tables

def test_model_initialization() -> None:
    """Verify basic instantiation of ORM models works without errors."""
    tick = IntradayTick(
        symbol="RELIANCE", 
        ltp=2500.0, 
        bid_price=2499.0, 
        ask_price=2501.0, 
        bid_qty=100.0, 
        ask_qty=150.0, 
        volume=2000.0
    )
    assert tick.symbol == "RELIANCE"
    assert tick.ltp == 2500.0

def test_alembic_offline_migration_validity() -> None:
    """
    Verify that Alembic can generate SQL for upgrade and downgrade safely.
    Offline mode tests syntax and migration validity without a live DB.
    """
    # Upgrade test
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Alembic upgrade SQL failed: {result.stderr}"
    assert "CREATE TABLE intraday_ticks" in result.stdout
    
    # Downgrade test
    result_down = subprocess.run(
        [sys.executable, "-m", "alembic", "downgrade", "head:base", "--sql"],
        capture_output=True,
        text=True
    )
    assert result_down.returncode == 0, f"Alembic downgrade SQL failed: {result_down.stderr}"
    assert "DROP TABLE intraday_ticks" in result_down.stdout
