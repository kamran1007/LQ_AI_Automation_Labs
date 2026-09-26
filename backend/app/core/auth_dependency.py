from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.services.auth_token_service import decode_access_token


security = HTTPBearer()


async def get_current_auth_session(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> AuthSession:

    token = credentials.credentials

    # --------------------------------------------------
    # Decode and validate JWT
    # --------------------------------------------------

    try:
        payload = decode_access_token(token)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------
    # Extract user_id
    # --------------------------------------------------

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing user_id",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------
    # Extract session_id
    # --------------------------------------------------

    session_id = payload.get("sid")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token missing session_id",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user_id in access token",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------
    # Find the exact authentication session
    # --------------------------------------------------

    result = await db.execute(
        select(AuthSession).where(
            AuthSession.user_id == user_id,
            AuthSession.session_id == session_id,
        )
    )

    session = result.scalar_one_or_none()

    # --------------------------------------------------
    # Session must exist
    # --------------------------------------------------

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session not found",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------
    # Session must not be revoked
    # --------------------------------------------------

    if session.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has been revoked",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # --------------------------------------------------
    # Session must not be expired
    # --------------------------------------------------

    from datetime import datetime, timezone

    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication session has expired",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    return session