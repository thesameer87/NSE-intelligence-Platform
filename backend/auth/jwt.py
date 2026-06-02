import jwt
from datetime import datetime, timedelta, timezone
from typing import Any

from backend.config import Settings
from backend.auth.exceptions import TokenExpiredError, InvalidTokenError

settings = Settings()  # type: ignore[call-arg]


def create_access_token(
    subject: str, 
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None
) -> str:
    """Creates a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expiry_minutes)
        
    to_encode = {"sub": subject, "exp": expire}
    if extra_claims:
        to_encode.update(extra_claims)
        
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decodes and validates a JWT access token."""
    try:
        # Explicitly enforce algorithm whitelist and require exp/sub claims
        # This prevents algorithm confusion (e.g., alg=none) and missing data
        payload = jwt.decode(
            token, 
            settings.jwt_secret, 
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]}
        )
        return dict(payload)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.PyJWTError:
        # Catches InvalidSignatureError, DecodeError (malformed structure), MissingRequiredClaimError
        raise InvalidTokenError("Could not validate credentials")
