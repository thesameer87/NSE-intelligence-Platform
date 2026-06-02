import os
import pytest
from pydantic import ValidationError
from backend.config import Settings

def test_missing_config_raises_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Clear out environment to simulate missing config
    monkeypatch.delenv("ANGEL_ONE_API_KEY", raising=False)
    monkeypatch.delenv("ANGEL_ONE_CLIENT_ID", raising=False)
    monkeypatch.delenv("ANGEL_ONE_PASSWORD", raising=False)
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("INTERNAL_API_TOKEN", raising=False)
    
    with pytest.raises(ValidationError):
        Settings(_env_file=None) # type: ignore

def test_valid_config(monkeypatch: pytest.MonkeyPatch) -> None:
    # Set all required variables
    monkeypatch.setenv("ANGEL_ONE_API_KEY", "test_api")
    monkeypatch.setenv("ANGEL_ONE_CLIENT_ID", "test_client")
    monkeypatch.setenv("ANGEL_ONE_PASSWORD", "test_pass")
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "test_jwt")
    monkeypatch.setenv("INTERNAL_API_TOKEN", "test_internal")
    monkeypatch.setenv("SCHEDULER_INTERVAL_SECONDS", "5")
    monkeypatch.setenv("ENVIRONMENT", "development")
    
    settings = Settings(_env_file=None) # type: ignore
    assert settings.angel_one_api_key == "test_api"
    assert settings.scheduler_interval_seconds == 5
    assert settings.environment == "development"

def test_invalid_type_raises_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANGEL_ONE_API_KEY", "test_api")
    monkeypatch.setenv("ANGEL_ONE_CLIENT_ID", "test_client")
    monkeypatch.setenv("ANGEL_ONE_PASSWORD", "test_pass")
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "test_jwt")
    monkeypatch.setenv("INTERNAL_API_TOKEN", "test_internal")
    
    # Pass a string where an integer is expected for interval
    monkeypatch.setenv("SCHEDULER_INTERVAL_SECONDS", "not_an_integer")
    
    with pytest.raises(ValidationError):
        Settings(_env_file=None) # type: ignore

def test_config_validator_success(monkeypatch: pytest.MonkeyPatch) -> None:
    # Test deterministic startup validation wrapper
    monkeypatch.setenv("ANGEL_ONE_API_KEY", "test_api")
    monkeypatch.setenv("ANGEL_ONE_CLIENT_ID", "test_client")
    monkeypatch.setenv("ANGEL_ONE_PASSWORD", "test_pass")
    monkeypatch.setenv("SUPABASE_URL", "http://localhost")
    monkeypatch.setenv("SUPABASE_KEY", "test_key")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost/db")
    monkeypatch.setenv("JWT_SECRET", "test_jwt")
    monkeypatch.setenv("INTERNAL_API_TOKEN", "test_internal")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SCHEDULER_INTERVAL_SECONDS", "60")
    
    from backend.config_validator import validate_configuration
    settings = validate_configuration(_env_file=None)
    assert settings.environment == "production"

def test_config_validator_fails_fast_on_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    # Ensures the startup wrapper raises appropriately
    monkeypatch.delenv("JWT_SECRET", raising=False)
    
    from backend.config_validator import validate_configuration
    with pytest.raises(ValidationError):
        validate_configuration(_env_file=None)
