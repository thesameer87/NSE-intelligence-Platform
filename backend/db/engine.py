from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from backend.config import Settings


def get_engine(db_url: str | None = None) -> AsyncEngine:
    """
    Creates an asynchronous SQLAlchemy engine.
    Relies on transparent configuration injection via Pydantic Settings.
    """
    settings = Settings()  # type: ignore[call-arg]
    url = db_url or settings.database_url

    return create_async_engine(
        url,
        echo=(settings.environment != "production"),
        future=True,
        pool_pre_ping=True,  # Validates connection on checkout
        pool_size=5,
        max_overflow=10,
    )


engine = get_engine()
