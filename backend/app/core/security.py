from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.services.auth_token_service import decode_access_token


bearer_scheme = HTTPBearer(
    auto_error=True
)


@dataclass
class AuthContext:
    user_id: int
    session_id: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def get_current_auth(
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:

    # ---------------------------------------------
    # 1. Get bearer token
    # ---------------------------------------------

    token = credentials.credentials

    # ---------------------------------------------
    # 2. Decode + validate JWT
    # ---------------------------------------------

    try:
        payload = decode_access_token(token)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ---------------------------------------------
    # 3. Extract claims
    # ---------------------------------------------

    user_id_raw = payload.get("sub")
    session_id = payload.get("sid")

    if not user_id_raw or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token claims",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:
        user_id = int(user_id_raw)

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identity",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ---------------------------------------------
    # 4. Find matching authentication session
    # ---------------------------------------------

    result = await db.execute(
        select(AuthSession).where(
            AuthSession.user_id == user_id,
            AuthSession.session_id == session_id,
        )
    )

    session = result.scalar_one_or_none()

    # ---------------------------------------------
    # 5. Session must exist
    # ---------------------------------------------

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session not found",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ---------------------------------------------
    # 6. Session must not be revoked
    # ---------------------------------------------

    if session.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has been revoked",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ---------------------------------------------
    # 7. Session must not be expired
    # ---------------------------------------------

    if session.expires_at <= utc_now():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has expired",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    # ---------------------------------------------
    # 8. Return authenticated context
    # ---------------------------------------------

    return AuthContext(
        user_id=user_id,
        session_id=session_id,
    )