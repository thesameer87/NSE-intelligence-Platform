from sqlalchemy.orm import DeclarativeBase

# The single declarative base for all ORM models.
# Absolutely no Base.metadata.create_all() will be called;
# Alembic handles all migrations safely.
class Base(DeclarativeBase):
    pass
