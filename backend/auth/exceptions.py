class AuthException(Exception):
    """Base exception for authentication errors."""

    pass


class InvalidCredentialsError(AuthException):
    """Raised when password verification fails."""

    pass


class TokenExpiredError(AuthException):
    """Raised when a JWT has expired."""

    pass


class InvalidTokenError(AuthException):
    """Raised when a JWT is invalid (malformed, bad signature, etc)."""

    pass


class MissingTokenError(AuthException):
    """Raised when no token is provided."""

    pass
