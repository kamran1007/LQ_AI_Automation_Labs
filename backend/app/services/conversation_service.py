from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


async def save_conversation(
    db: AsyncSession,
    user_id: int,
    message: str,
    ai_response: str,
    intent: str,
    extra_data: dict | None = None,
):
    conversation = Conversation(
        user_id=user_id,
        message=message,
        ai_response=ai_response,
        intent=intent,
        extra_data=extra_data,
    )

    db.add(conversation)

    await db.commit()
    await db.refresh(conversation)

    return conversation


async def get_recent_conversations(
    db: AsyncSession,
    user_id: int,
    limit: int = 5,
):
    query = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id
        )
        .order_by(
            Conversation.created_at.desc()
        )
        .limit(limit)
    )

    result = await db.execute(query)

    conversations = result.scalars().all()

    return list(reversed(conversations))


async def get_active_appointment_state(
    db: AsyncSession,
    user_id: int,
):
    """
    Get the latest persisted appointment booking state.

    IMPORTANT:
    We only return the booking_state saved inside
    Conversation.extra_data.
    """

    query = (
        select(Conversation)
        .where(
            Conversation.user_id == user_id,
            Conversation.intent == "appointment_booking",
        )
        .order_by(
            Conversation.created_at.desc()
        )
        .limit(1)
    )

    result = await db.execute(query)

    conversation = result.scalar_one_or_none()

    if not conversation:
        print(
            "ACTIVE BOOKING STATE: "
            "NO APPOINTMENT CONVERSATION FOUND"
        )
        return None

    extra_data = conversation.extra_data or {}

    booking_state = extra_data.get(
        "booking_state"
    )

    print(
        "\n========== PERSISTED BOOKING STATE =========="
    )

    print(
        "CONVERSATION ID:",
        conversation.id,
    )

    print(
        "USER ID:",
        conversation.user_id,
    )

    print(
        "MESSAGE:",
        conversation.message,
    )

    print(
        "BOOKING STATE:",
        booking_state,
    )

    print(
        "==============================================\n"
    )

    return booking_state