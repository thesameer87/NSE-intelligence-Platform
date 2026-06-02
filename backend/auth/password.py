import bcrypt


def hash_password(password: str) -> str:
    """
    Hashes a plaintext password using bcrypt.
    
    Salts are securely generated on the fly via bcrypt.gensalt().
    The resulting hash string natively encodes the algorithm version, 
    cost factor, salt, and hash data deterministically.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plaintext password against a bcrypt hash.
    
    This function uses bcrypt.checkpw which performs a constant-time
    comparison, mitigating timing attacks.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), 
        hashed_password.encode("utf-8")
    )
