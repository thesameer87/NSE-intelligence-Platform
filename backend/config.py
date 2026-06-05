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


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
