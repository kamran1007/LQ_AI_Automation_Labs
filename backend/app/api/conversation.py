from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.auth_session import AuthSession
from app.schemas.conversation_schema import ConversationResponse
from app.services.conversation_service import get_user_conversations
from app.core.auth_dependency import get_current_auth_session


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get(
    "",
    response_model=list[ConversationResponse],
)
async def get_my_conversations(
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    auth_session: AuthSession = Depends(
        get_current_auth_session
    ),
    db: AsyncSession = Depends(get_db),
):
    conversations = await get_user_conversations(
        db=db,
        user_id=auth_session.user_id,
        limit=limit,
        offset=offset,
    )

    return conversations