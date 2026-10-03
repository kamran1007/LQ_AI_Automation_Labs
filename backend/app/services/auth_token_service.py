import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt


JWT_SECRET = os.getenv("AUTH_JWT_SECRET")
JWT_ALGORITHM = os.getenv("AUTH_JWT_ALGORITHM", "HS256")

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", "15")
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("AUTH_REFRESH_TOKEN_EXPIRE_DAYS", "30")
)


if not JWT_SECRET:
    raise RuntimeError(
        "AUTH_JWT_SECRET is not configured"
    )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(
    user_id: int,
    session_id: str,
    role_id: int | None = None, 
    hospital_id: int | None = None,
) -> str:
    """
    Create a short-lived JWT access token.

    The access token contains:
    - sub: user ID
    - sid: session ID
    - type: access
    - iat: issued at
    - exp: expiration
    """

    now = utc_now()

    expires_at = (
        now
        + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    payload = {
        "sub": str(user_id),
        "sid": session_id,
        "type": "access",
        "iat": now,
        "exp": expires_at,
    }
    # Hospital-scoped authentication context 
    if role_id is not None: 
        payload["role_id"] = role_id
        
    if hospital_id is not None: 
        payload["hospital_id"] = hospital_id

    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def create_refresh_token() -> str:
    """
    Generate a cryptographically secure opaque refresh token.

    The raw token is returned to the client.
    Only its SHA-256 hash should be stored in the database.
    """

    return secrets.token_urlsafe(64)


def hash_refresh_token(
    refresh_token: str,
) -> str:
    """
    Hash refresh token before storing it in the database.
    """

    return hashlib.sha256(
        refresh_token.encode("utf-8")
    ).hexdigest()


def get_refresh_token_expiry() -> datetime:
    """
    Return the expiration time for a new refresh token.
    """

    return (
        utc_now()
        + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )


def decode_access_token(
    token: str,
) -> dict:
    """
    Decode and validate an access JWT.
    """

    payload = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
    )

    if payload.get("type") != "access":
        raise ValueError(
            "Invalid token type"
        )

    return payload