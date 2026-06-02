class PersistenceError(Exception):
    """Base exception for all persistence layer errors."""

    pass


class DatabaseOperationError(PersistenceError):
    """Raised when an ORM or underlying database operation fails."""

    pass
