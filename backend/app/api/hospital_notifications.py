from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.notification import Notification
from app.api.hospital import get_current_hospital_context


router = APIRouter(
    prefix="/hospital",
    tags=["Hospital Notifications"],
)


# =========================================================
# GET HOSPITAL NOTIFICATIONS
# =========================================================

@router.get("/notifications")
async def get_hospital_notifications(
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    hospital_id = context["hospital_id"]

    result = await db.execute(
        select(Notification)
        .where(
            Notification.hospital_id == hospital_id
        )
        .order_by(
            Notification.created_at.desc()
        )
    )

    notifications = result.scalars().all()

    return {
        "success": True,
        "data": [
            {
                "id": notification.id,
                "hospital_id": notification.hospital_id,
                "appointment_request_id": notification.appointment_request_id,
                "type": notification.type,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at,
                "read_at": notification.read_at,
            }
            for notification in notifications
        ],
    }


# =========================================================
# GET UNREAD NOTIFICATION COUNT
# =========================================================

@router.get("/notifications/unread-count")
async def get_unread_notification_count(
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    hospital_id = context["hospital_id"]

    result = await db.execute(
        select(func.count(Notification.id))
        .where(
            Notification.hospital_id == hospital_id,
            Notification.is_read == False,
        )
    )

    unread_count = result.scalar() or 0

    return {
        "success": True,
        "unread_count": unread_count,
    }


# =========================================================
# MARK NOTIFICATION AS READ
# =========================================================

@router.post("/notifications/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    hospital_id = context["hospital_id"]

    result = await db.execute(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.hospital_id == hospital_id,
        )
    )

    notification = result.scalar_one_or_none()

    if notification is None:
        raise HTTPException(
            status_code=404,
            detail="Notification not found.",
        )

    if not notification.is_read:
        notification.is_read = True
        notification.read_at = func.now()

        await db.commit()
        await db.refresh(notification)

    return {
        "success": True,
        "message": "Notification marked as read.",
        "data": {
            "id": notification.id,
            "is_read": notification.is_read,
            "read_at": notification.read_at,
        },
    }


# =========================================================
# MARK ALL NOTIFICATIONS AS READ
# =========================================================

@router.post("/notifications/read-all")
async def mark_all_notifications_as_read(
    db: AsyncSession = Depends(get_db),
    context=Depends(get_current_hospital_context),
):
    hospital_id = context["hospital_id"]

    result = await db.execute(
        select(Notification).where(
            Notification.hospital_id == hospital_id,
            Notification.is_read == False,
        )
    )

    notifications = result.scalars().all()

    for notification in notifications:
        notification.is_read = True
        notification.read_at = func.now()

    await db.commit()

    return {
        "success": True,
        "message": "All notifications marked as read.",
        "updated_count": len(notifications),
    }