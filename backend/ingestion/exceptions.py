class IngestionError(Exception):
    """Base exception for all ingestion-related errors."""

    pass


class SmartAPIError(IngestionError):
    """Raised when the SmartAPI client encounters an error (HTTP or logical)."""

    pass


class IngestionValidationError(IngestionError):
    """Raised when payload normalization or validation fails."""

    pass
