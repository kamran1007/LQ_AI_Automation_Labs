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
    get_active_appointment_state,
)

from app.services.appointment_request_service import (
    create_appointment_request,
)

from app.db.session import get_db

from app.workflows.workflow_router import (
    route_workflow,
)

from datetime import datetime


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
    # 1. LOAD CHAT HISTORY
    # =====================================================

    history = await get_recent_conversations(
        db=db,
        user_id=request.user_id,
    )

    # =====================================================
    # 2. LOAD ACTIVE APPOINTMENT STATE
    # =====================================================

    booking_state = await get_active_appointment_state(
        db=db,
        user_id=request.user_id,
    )

    print("\n======================================")
    print("CHAT REQUEST")
    print("USER ID:", request.user_id)
    print("MESSAGE:", request.message)
    print("ACTIVE BOOKING STATE:")
    print(booking_state)
    print("======================================\n")

    # =====================================================
    # 3. ASK AI
    # =====================================================

    ai_response = ask_ai(
        message=request.message,
        history=history,
    )

    print("\n======================================")
    print("AI RESPONSE BEFORE BACKEND ROUTING")
    print(ai_response)
    print("======================================\n")

    # =====================================================
    # 4. BACKEND WORKFLOW ROUTER
    # =====================================================

    ai_response = await route_workflow(
        ai_response=ai_response,
        db=db,
        user_message=request.message,
        user_id=request.user_id,
        booking_state=booking_state,
    )

    print("\n======================================")
    print("AI RESPONSE AFTER BACKEND ROUTING")
    print(ai_response)
    print("======================================\n")

    # =====================================================
    # 5. GET UPDATED BOOKING STATE
    # =====================================================

    booking_state = ai_response.get(
        "booking_state"
    )

    print("\n======================================")
    print("UPDATED BOOKING STATE")
    print(booking_state)
    print("======================================\n")

    # =====================================================
    # 6. FINAL APPOINTMENT REQUEST
    # =====================================================

    workflow = (
        ai_response.get("workflow")
        or {}
    )

    if (
        workflow.get("action")
        == "create_appointment_request"
    ):

        if not booking_state:
            raise ValueError(
                "Cannot create appointment request: "
                "booking state is missing."
            )

        doctor = booking_state.get("doctor")

        appointment = booking_state.get(
            "appointment"
        )

        if not doctor:
            raise ValueError(
                "Cannot create appointment request: "
                "doctor information is missing."
            )

        if not appointment:
            raise ValueError(
                "Cannot create appointment request: "
                "appointment information is missing."
            )

        requested_start_at = (
            appointment.get(
                "requested_start_at"
            )
        )

        if not requested_start_at:
            raise ValueError(
                "Cannot create appointment request: "
                "requested_start_at is missing."
            )

        # JSON state stores datetime as ISO string.
        if isinstance(
            requested_start_at,
            str,
        ):
            requested_start_at = (
                datetime.fromisoformat(
                    requested_start_at
                )
            )

        appointment_request = (
            await create_appointment_request(
                db=db,
                patient_id=request.user_id,
                hospital_id=doctor["hospital_id"],
                doctor_id=doctor["id"],
                requested_start_at=(
                    requested_start_at
                ),
                conversation_id=None,
                duration_minutes=(
                    appointment.get(
                        "duration_minutes",
                        30,
                    )
                ),
                patient_message=(
                    booking_state.get(
                        "patient_message"
                    )
                ),
            )
        )

        ai_response["success"] = True

        ai_response["message"] = (
            f"Your appointment request has been "
            f"sent to {doctor['name']}.\n\n"
            f"Appointment Request ID: "
            f"#{appointment_request.id}"
        )

        ai_response["workflow"] = {
            "step": "completed",
            "appointment_request_id": (
                appointment_request.id
            ),
        }

        ai_response["metadata"] = {
            "appointment_request_id": (
                appointment_request.id
            ),
            "doctor_id": (
                appointment_request.doctor_id
            ),
            "hospital_id": (
                appointment_request.hospital_id
            ),
            "requested_start_at": (
                appointment_request
                .requested_start_at
                .isoformat()
            ),
            "duration_minutes": (
                appointment_request
                .duration_minutes
            ),
            "status": (
                appointment_request.status
            ),
        }

        booking_state = None

        ai_response[
            "booking_state"
        ] = None

    # =====================================================
    # 7. SAVE CONVERSATION + BOOKING STATE
    # =====================================================

    print("\n======================================")
    print("SAVING CONVERSATION")
    print("BOOKING STATE TO SAVE:")
    print(booking_state)
    print("======================================\n")

    await save_conversation(
        db=db,
        user_id=request.user_id,
        message=request.message,
        ai_response=ai_response["message"],
        intent=ai_response["intent"],
        extra_data={
            "metadata": (
                ai_response.get(
                    "metadata"
                )
            ),
            "booking_state": booking_state,
        },
    )

    return ChatResponse(
        **ai_response
    )