from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.db.engine import engine

# Create the sessionmaker factory
async_session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides an asynchronous database session.
    Automatically closes the session when the request finishes or fails.
    """
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
