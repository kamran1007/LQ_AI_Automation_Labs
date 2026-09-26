from datetime import datetime, timezone
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth_session import AuthSession
from app.services.auth_token_service import (
    create_access_token,
    create_refresh_token,
    get_refresh_token_expiry,
    hash_refresh_token,
)

def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def create_auth_session(
    db: AsyncSession,
    user_id: int,
    device_name: str | None = None,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> dict:
    """
    Create a new authenticated session.

    Returns:
        access_token
        refresh_token
        session_id
        expires_at
    """

    # -----------------------------------------
    # Generate session ID
    # -----------------------------------------

    import secrets

    session_id = secrets.token_urlsafe(32)

    # -----------------------------------------
    # Generate refresh token
    # -----------------------------------------

    refresh_token = create_refresh_token()

    refresh_token_hash = hash_refresh_token(
        refresh_token
    )

    # -----------------------------------------
    # Session expiration
    # -----------------------------------------

    expires_at = get_refresh_token_expiry()

    # -----------------------------------------
    # Create DB session
    # -----------------------------------------

    session = AuthSession(
        user_id=user_id,
        session_id=session_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        last_used_at=utc_now(),
        is_revoked=False,
        device_name=device_name,
        user_agent=user_agent,
        ip_address=ip_address,
    )

    db.add(session)

    await db.commit()

    await db.refresh(session)

    # -----------------------------------------
    # Create access token
    # -----------------------------------------

    access_token = create_access_token(
        user_id=user_id,
        session_id=session_id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "session_id": session_id,
        "expires_at": expires_at,
    }


async def get_valid_session_by_refresh_token(
    db: AsyncSession,
    refresh_token: str,
) -> AuthSession | None:
    """
    Find a valid session using a refresh token.

    The raw refresh token is NEVER stored in DB.
    """

    refresh_token_hash = hash_refresh_token(
        refresh_token
    )

    result = await db.execute(
        select(AuthSession).where(
            AuthSession.refresh_token_hash
            == refresh_token_hash
        )
    )

    session = result.scalar_one_or_none()

    if session is None:
        return None

    # -----------------------------------------
    # Revoked session
    # -----------------------------------------

    if session.is_revoked:
        return None

    # -----------------------------------------
    # Expired session
    # -----------------------------------------

    if session.expires_at <= utc_now():
        return None

    return session


async def update_session_last_used(
    db: AsyncSession,
    session: AuthSession,
) -> AuthSession:
    """
    Update the last-used timestamp.
    """

    session.last_used_at = utc_now()

    await db.commit()

    await db.refresh(session)

    return session


async def revoke_session(
    db: AsyncSession,
    session: AuthSession,
    reason: str | None = None,
) -> AuthSession:
    """
    Revoke an authentication session.
    """

    if session.is_revoked:
        return session

    session.is_revoked = True
    session.revoked_at = utc_now()
    session.revoked_reason = reason

    await db.commit()

    await db.refresh(session)

    return session


async def revoke_session_by_refresh_token(
    db: AsyncSession,
    refresh_token: str,
    reason: str | None = None,
) -> bool:
    """
    Revoke a session using its refresh token.
    """

    session = await get_valid_session_by_refresh_token(
        db,
        refresh_token,
    )

    if session is None:
        return False

    await revoke_session(
        db,
        session,
        reason=reason,
    )

    return True


async def rotate_auth_session(
    db: AsyncSession,
    session: AuthSession,
) -> dict:
    """
    Rotate a refresh token.

    The existing session is revoked and a new session is created.

    Returns:
        access_token
        refresh_token
        session_id
        expires_at
    """

    # --------------------------------------------------
    # Generate NEW session ID
    # --------------------------------------------------

    new_session_id = secrets.token_urlsafe(32)

    # --------------------------------------------------
    # Generate NEW refresh token
    # --------------------------------------------------

    new_refresh_token = create_refresh_token()

    new_refresh_token_hash = hash_refresh_token(
        new_refresh_token
    )

    # --------------------------------------------------
    # Generate NEW expiration
    # --------------------------------------------------

    new_expires_at = get_refresh_token_expiry()

    # --------------------------------------------------
    # Revoke OLD session
    # --------------------------------------------------

    session.is_revoked = True
    session.revoked_at = utc_now()
    session.revoked_reason = "refresh_token_rotated"

    # --------------------------------------------------
    # Link OLD → NEW session
    # --------------------------------------------------

    session.replaced_by_session_id = new_session_id

    # --------------------------------------------------
    # Create NEW session
    # --------------------------------------------------

    new_session = AuthSession(
        user_id=session.user_id,
        session_id=new_session_id,
        refresh_token_hash=new_refresh_token_hash,
        expires_at=new_expires_at,
        last_used_at=utc_now(),
        is_revoked=False,

        # Carry device information forward
        device_name=session.device_name,
        user_agent=session.user_agent,
        ip_address=session.ip_address,
    )

    db.add(new_session)

    # --------------------------------------------------
    # Commit both changes atomically
    # --------------------------------------------------

    await db.commit()

    await db.refresh(new_session)

    # --------------------------------------------------
    # Create NEW access token
    # --------------------------------------------------

    access_token = create_access_token(
        user_id=session.user_id,
        session_id=new_session_id,
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "session_id": new_session_id,
        "expires_at": new_expires_at,
    }