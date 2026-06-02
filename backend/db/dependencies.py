from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import get_db_session

# Reusable FastAPI dependency for database sessions
DBSession = Annotated[AsyncSession, Depends(get_db_session)]

__all__ = ["get_db_session", "DBSession"]
