from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.chat_schema import (
    ChatRequest,
    ChatResponse,
)

from app.services.openai_service import ask_ai

from app.services.conversation_service import (
    save_conversation,
    get_recent_conversations,
)

from app.db.session import get_db

from app.workflows.workflow_router import (
    route_workflow,
)


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):

    # =====================================================
    # GET CONVERSATION HISTORY
    # =====================================================

    history = await get_recent_conversations(
        db=db,
        user_id=request.user_id,
    )

    # =====================================================
    # ASK AI
    # =====================================================

    ai_response = ask_ai(
        message=request.message,
        history=history,
    )

    # =====================================================
    # ROUTE BACKEND WORKFLOW
    # =====================================================

    ai_response = await route_workflow(
        ai_response,
        db,
        user_message=request.message,
    )

    # =====================================================
    # SAVE CONVERSATION
    # =====================================================

    await save_conversation(
        db=db,
        user_id=request.user_id,
        message=request.message,
        ai_response=ai_response["message"],
        intent=ai_response["intent"],
        extra_data=ai_response.get("metadata"),
    )

    # =====================================================
    # RETURN RESPONSE
    # =====================================================

    return ChatResponse(
        **ai_response
    )