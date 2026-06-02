import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from backend.db.engine import get_engine, engine
from backend.db.session import async_session_maker, get_db_session

def test_engine_initialization() -> None:
    """Validate engine configures correctly without implicit mutation."""
    assert isinstance(engine, AsyncEngine)

@pytest.mark.asyncio
async def test_session_creation() -> None:
    """Validate the session factory issues standard async sessions."""
    session = async_session_maker()
    assert isinstance(session, AsyncSession)
    await session.close()

@pytest.mark.asyncio
async def test_get_db_session_dependency() -> None:
    """Validate the FastAPI dependency lifecycle."""
    gen = get_db_session()
    session = await anext(gen)
    assert isinstance(session, AsyncSession)
    await session.close()
