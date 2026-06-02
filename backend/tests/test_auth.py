from datetime import timedelta

import jwt
import pytest

from backend.auth.exceptions import InvalidTokenError, TokenExpiredError
from backend.auth.jwt import create_access_token, decode_access_token
from backend.auth.password import hash_password, verify_password
from backend.config import Settings

settings = Settings()  # type: ignore[call-arg]


def test_password_hashing() -> None:
    """Test password hashing and verification."""
    password = "super_secure_password"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_create_and_decode_jwt() -> None:
    """Test JWT creation and decoding."""
    subject = "user123"
    token = create_access_token(subject=subject)

    payload = decode_access_token(token)
    assert payload["sub"] == subject
    assert "exp" in payload


def test_jwt_expiry() -> None:
    """Test that expired JWTs raise TokenExpiredError."""
    # Create token expired 1 minute ago
    token = create_access_token(subject="test", expires_delta=timedelta(minutes=-1))

    with pytest.raises(TokenExpiredError):
        decode_access_token(token)


def test_jwt_invalid_signature() -> None:
    """Test that invalid JWT signatures raise InvalidTokenError."""
    token = create_access_token(subject="test")
    # Tamper with token
    invalid_token = token[:-5] + "aaaaa"

    with pytest.raises(InvalidTokenError):
        decode_access_token(invalid_token)


def test_jwt_missing_subject() -> None:
    """Test token lacking 'sub' claim."""
    # Create manually with exp only
    to_encode = {"exp": 9999999999}
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_jwt_missing_exp() -> None:
    """Test token lacking 'exp' claim."""
    # Create manually with sub only
    to_encode = {"sub": "user"}
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_jwt_wrong_algorithm() -> None:
    """Test token signed with a different algorithm (e.g., HS512) is rejected."""
    to_encode = {"sub": "user", "exp": 9999999999}
    token = jwt.encode(to_encode, settings.jwt_secret, algorithm="HS512")
    
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
