from datetime import datetime, timezone

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.hospital import Hospital
from app.models.auth_session import AuthSession

from app.schemas.hospital_schema import HospitalMeResponse

from app.services.auth_token_service import decode_access_token
from app.models.appointment_request import AppointmentRequest


router = APIRouter(
    tags=["Hospital"],
)

security = HTTPBearer()


async def get_current_hospital_context(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    # ---------------------------------------------------------
    # 1. Read access token
    # ---------------------------------------------------------

    token = credentials.credentials

    # ---------------------------------------------------------
    # 2. Decode and validate JWT
    # ---------------------------------------------------------

    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # 3. Extract JWT claims
    # ---------------------------------------------------------

    user_id = payload.get("sub")
    session_id = payload.get("sid")
    token_type = payload.get("type")
    role_id = payload.get("role_id")
    hospital_id = payload.get("hospital_id")

    if not user_id or not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if role_id is None or hospital_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token is not hospital-scoped",
        )

    try:
        user_id = int(user_id)
        role_id = int(role_id)
        hospital_id = int(hospital_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
        )

    # ---------------------------------------------------------
    # 4. Validate session
    # ---------------------------------------------------------

    session_result = await db.execute(
        select(AuthSession).where(
            AuthSession.session_id == session_id,
            AuthSession.user_id == user_id,
            AuthSession.is_revoked == False,
            AuthSession.expires_at > datetime.now(timezone.utc),
        )
    )

    auth_session = session_result.scalar_one_or_none()

    if auth_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid, revoked, or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ---------------------------------------------------------
    # 5. Find user
    # ---------------------------------------------------------

    user_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active == True,
        )
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or does not exist",
        )

    # ---------------------------------------------------------
    # 6. Validate user + role + hospital combination
    # ---------------------------------------------------------

    role_result = await db.execute(
        select(UserRole, Role)
        .join(
            Role,
            Role.id == UserRole.role_id,
        )
        .where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
            UserRole.hospital_id == hospital_id,
        )
    )

    role_data = role_result.first()

    if role_data is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not authorized for this hospital",
        )

    user_role, role = role_data

    # ---------------------------------------------------------
    # 7. Validate hospital
    # ---------------------------------------------------------

    hospital_result = await db.execute(
        select(Hospital).where(
            Hospital.id == hospital_id,
            Hospital.is_active == True,
        )
    )

    hospital = hospital_result.scalar_one_or_none()

    if hospital is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital is inactive or does not exist",
        )

    # ---------------------------------------------------------
    # 8. Return complete authenticated context
    # ---------------------------------------------------------

    return {
        "user": user,
        "role": role,
        "hospital": hospital,
        "session": auth_session,
        "user_id": user_id,
        "role_id": role_id,
        "hospital_id": hospital_id,
        "session_id": session_id,
    }


@router.get(
    "/me",
    response_model=HospitalMeResponse,
)
async def hospital_me(
    context=Depends(get_current_hospital_context),
):
    user = context["user"]
    role = context["role"]
    hospital = context["hospital"]

    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "email": user.email,
        },
        "role": {
            "id": role.id,
            "name": role.name,
        },
        "hospital": {
            "id": hospital.id,
            "name": hospital.name,
            "phone": hospital.phone,
            "email": hospital.email,
            "address": hospital.address,
            "city": hospital.city,
            "state": hospital.state,
            "country": hospital.country,
            "timezone": hospital.timezone,
            "is_verified": hospital.is_verified,
            "is_active": hospital.is_active,
        },
        "session_id": context["session_id"],
    }


@router.get("/dashboard")
async def hospital_dashboard(
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    hospital_id = context["hospital_id"]
    hospital = context["hospital"]

    total_result = await db.execute(
        select(func.count(AppointmentRequest.id)).where(
            AppointmentRequest.hospital_id == hospital_id
        )
    )

    pending_result = await db.execute(
        select(func.count(AppointmentRequest.id)).where(
            AppointmentRequest.hospital_id == hospital_id,
            AppointmentRequest.status == "pending",
        )
    )

    accepted_result = await db.execute(
        select(func.count(AppointmentRequest.id)).where(
            AppointmentRequest.hospital_id == hospital_id,
            AppointmentRequest.status == "accepted",
        )
    )

    declined_result = await db.execute(
        select(func.count(AppointmentRequest.id)).where(
            AppointmentRequest.hospital_id == hospital_id,
            AppointmentRequest.status == "declined",
        )
    )

    proposed_result = await db.execute(
        select(func.count(AppointmentRequest.id)).where(
            AppointmentRequest.hospital_id == hospital_id,
            AppointmentRequest.status == "proposed",
        )
    )

    return {
        "success": True,
        "hospital": {
            "id": hospital.id,
            "name": hospital.name,
        },
        "stats": {
            "total_appointments": total_result.scalar() or 0,
            "pending_appointments": pending_result.scalar() or 0,
            "accepted_appointments": accepted_result.scalar() or 0,
            "declined_appointments": declined_result.scalar() or 0,
            "proposed_appointments": proposed_result.scalar() or 0,
        },
    }