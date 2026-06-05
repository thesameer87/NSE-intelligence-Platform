from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    environment: Literal["development", "staging", "production"] = "development"
    scheduler_interval_seconds: int = Field(default=5, ge=1)
    
    # Angel One
    angel_one_base_url: str = "https://apiconnect.angelbroking.com"
    angel_one_api_key: str
    angel_one_client_id: str
    angel_one_password: str
    angel_one_totp_secret: str
    
    # Supabase / Database
    supabase_url: str
    supabase_key: str
    database_url: str
    
    # Security
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = Field(default=15, ge=1)
    internal_api_token: str
    
    # Observability
    sentry_dsn: str | None = None

    # Intelligence Runtime
    rolling_window_size: int = Field(default=100, ge=50, description="Size of the rolling window buffer per symbol")
    signal_confidence_threshold: float = Field(default=0.75, ge=0.5, le=1.0)
    signal_min_expected_return: float = Field(default=0.005, ge=0.0)
    signal_regression_alignment_threshold: float = Field(default=0.6, ge=0.5, le=1.0)
    monitored_symbols: list[str] = Field(
        default=["RELIANCE-EQ", "TCS-EQ", "HDFCBANK-EQ", "INFY-EQ", "ICICIBANK-EQ"]
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
