from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation


async def save_conversation(
    db: AsyncSession,
    user_id: str,
    message: str,
    ai_response: str,
    intent: str,
    extra_data: dict | None = None
):

    conversation = Conversation(
        user_id=user_id,
        message=message,
        ai_response=ai_response,
        intent=intent,
        extra_data=extra_data
    )

    db.add(conversation)

    await db.commit()

    await db.refresh(conversation)

    return conversation

async def get_recent_conversations(
    db: AsyncSession,
    user_id: str,
    limit: int = 5
):

    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.created_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)

    conversations = result.scalars().all()

    return list(reversed(conversations))