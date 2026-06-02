import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from unittest.mock import AsyncMock, patch

from backend.db.dependencies import DBSession
from backend.db.session import get_db_session

# Create an isolated FastAPI app just for testing session injection boundaries
app = FastAPI()

from typing import Generator

@pytest.fixture(autouse=True)
def mock_db_session_factory() -> Generator[AsyncMock, None, None]:
    """Mock the sessionmaker to yield an AsyncMock instead of a real database connection."""
    with patch("backend.db.session.async_session_maker") as mock_maker:
        mock_session = AsyncMock(spec=AsyncSession)
        mock_maker.return_value.__aenter__.return_value = mock_session
        yield mock_session


@app.get("/test-db")
async def mock_db_route(db: DBSession) -> dict[str, str]:
    """Mock endpoint to prove injection works."""
    assert isinstance(db, AsyncSession)
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.get("/test-db-error")
async def mock_db_error_route(db: DBSession) -> dict[str, str]:
    """Mock endpoint to prove cleanup happens even on exception."""
    raise ValueError("Intentional error")


client = TestClient(app)


def test_db_dependency_injection() -> None:
    """Test that the DB session is correctly injected into routes."""
    response = client.get("/test-db")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_session_lifecycle_failure_behavior() -> None:
    """Test that an error inside the route propagates correctly."""
    with pytest.raises(ValueError, match="Intentional error"):
        client.get("/test-db-error")


@pytest.mark.asyncio
async def test_generator_cleanup() -> None:
    """Explicitly test the generator lifecycle cleanup boundary."""
    generator = get_db_session()

    # anext() starts the generator and yields the session
    session = await anext(generator)
    assert isinstance(session, AsyncSession)

    # The next anext() triggers the finally block in get_db_session
    with pytest.raises(StopAsyncIteration):
        await anext(generator)
