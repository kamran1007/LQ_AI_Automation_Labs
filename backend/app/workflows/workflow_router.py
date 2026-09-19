import re
from datetime import datetime, time
from zoneinfo import ZoneInfo

from app.services.doctor_search_service import (
    search_doctors,
    search_doctors_by_specialization,
)
from app.workflows.medicine_workflow import handle_medicine_workflow
from app.utils.date_time_utils import resolve_relative_date


IST = ZoneInfo("Asia/Kolkata")


# =========================================================
# BASIC HELPERS
# =========================================================

def is_yes(message: str) -> bool:
    return message.strip().lower() in {
        "yes", "yeah", "yep", "yup", "sure",
        "okay", "ok", "confirm", "confirmed",
        "go ahead", "continue",
    }


def is_no(message: str) -> bool:
    return message.strip().lower() in {
        "no", "nope", "nah", "cancel", "stop",
    }


def is_skip(message: str) -> bool:
    return message.strip().lower() in {
        "skip", "none", "nothing", "no note", "no",
        "nope", "nah",
    }


# =========================================================
# TIME / DATE HELPERS
# =========================================================

def normalize_time(time_text: str | None) -> str | None:
    if not time_text:
        return None

    value = time_text.strip().upper()

    match = re.fullmatch(r"(\d{1,2}):(\d{2})", value)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    value = re.sub(r"\s+", " ", value)

    match = re.fullmatch(
        r"(\d{1,2})(?::(\d{2}))?\s*(AM|PM)",
        value,
    )
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        period = match.group(3)

        if not 1 <= hour <= 12 or not 0 <= minute <= 59:
            return None

        if period == "AM":
            hour = 0 if hour == 12 else hour
        else:
            hour = 12 if hour == 12 else hour + 12

        return f"{hour:02d}:{minute:02d}"

    return None


def build_requested_start_at(
    appointment_date,
    time_text: str | None,
) -> datetime | None:
    normalized = normalize_time(time_text)
    if not normalized:
        return None

    hour, minute = map(int, normalized.split(":"))

    return datetime.combine(
        appointment_date,
        time(hour=hour, minute=minute),
        tzinfo=IST,
    )


def normalize_date_expression(value: str | None) -> str:
    if not value:
        return ""

    text = " ".join(value.lower().strip().split())

    replacements = {
        "tommorow": "tomorrow",
        "tomorow": "tomorrow",
        "tommorrow": "tomorrow",
        "day after tommorow": "day after tomorrow",
        "day after tomorow": "day after tomorrow",
        "day after tommorrow": "day after tomorrow",
    }

    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)

    return text


def extract_date_expression(text: str) -> str:
    normalized = normalize_date_expression(text)

    if "day after tomorrow" in normalized:
        return "day after tomorrow"
    if "tomorrow" in normalized:
        return "tomorrow"
    if re.search(r"\btoday\b", normalized):
        return "today"

    return ""


def extract_time_from_text(text: str) -> str | None:
    if not text:
        return None

    match = re.search(
        r"\b(?:at\s+)?(\d{1,2}(?::\d{2})?\s*(?:AM|PM))\b",
        text,
        re.IGNORECASE,
    )
    if match:
        return normalize_time(match.group(1))

    match = re.search(
        r"\b(?:at\s+)?([01]?\d|2[0-3]):[0-5]\d\b",
        text,
        re.IGNORECASE,
    )
    if match:
        return normalize_time(match.group(0))

    return None


# =========================================================
# DOCTOR SEARCH
# =========================================================

def extract_doctor_query(message: str) -> str:
    if not message:
        return ""

    text = message.strip()

    match = re.search(
        r"\bdr\.?\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        text,
        re.IGNORECASE,
    )
    if match:
        query = match.group(1).strip()
        return re.split(
            r"\b(?:for|at|on|tomorrow|today|please|day)\b",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

    match = re.search(
        r"\bdoctor\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        text,
        re.IGNORECASE,
    )
    if match:
        query = match.group(1).strip()
        return re.split(
            r"\b(?:for|at|on|tomorrow|today|please|day)\b",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

    return ""


def create_doctor_message(doctors: list[dict]) -> str:
    if not doctors:
        return (
            "I could not find an active doctor matching "
            "your search. Please provide another doctor's "
            "name, hospital name, or medical specialization."
        )

    if len(doctors) == 1:
        doctor = doctors[0]
        city = f", {doctor['city']}" if doctor.get("city") else ""
        return (
            f"I found {doctor['doctor_name']} — "
            f"{doctor['specialization']} at "
            f"{doctor['hospital_name']}{city}. "
            "Would you like to continue with this doctor?"
        )

    lines = [
        "I found multiple doctors matching your search. "
        "Please select the doctor you would like to consult:"
    ]

    for index, doctor in enumerate(doctors, start=1):
        city = f" — {doctor['city']}" if doctor.get("city") else ""
        lines.append(
            f"{index}. {doctor['doctor_name']} — "
            f"{doctor['specialization']} — "
            f"{doctor['hospital_name']}{city}"
        )

    return "\n".join(lines)


# =========================================================
# BOOKING STATE
# =========================================================

def create_booking_state(
    doctor: dict,
    workflow: dict | None = None,
    user_message: str = "",
) -> dict:
    workflow = workflow or {}

    date_expression = normalize_date_expression(
        workflow.get("date_expression")
        or extract_date_expression(user_message)
    )

    time_text = (
        workflow.get("time")
        or extract_time_from_text(user_message)
        or ""
    )

    appointment = {
        "date_expression": date_expression or None,
        "date": None,
        "day": None,
        "time": normalize_time(time_text),
        "requested_start_at": None,
        "duration_minutes": workflow.get("duration_minutes", 30),
    }

    if date_expression:
        appointment_date = resolve_relative_date(date_expression)

        if appointment_date:
            appointment["date"] = appointment_date.strftime("%d/%m/%Y")
            appointment["day"] = appointment_date.strftime("%A")

            requested_start_at = build_requested_start_at(
                appointment_date,
                time_text,
            )
            if requested_start_at:
                # JSON-safe: Conversation.extra_data is persisted as JSON.
                appointment["requested_start_at"] = (
                    requested_start_at.isoformat()
                )

    return {
        "step": "doctor_confirmation",
        "doctor": {
            "id": doctor["doctor_id"],
            "name": doctor["doctor_name"],
            "specialization": doctor["specialization"],
            "hospital_id": doctor["hospital_id"],
            "hospital_name": doctor["hospital_name"],
            "city": doctor.get("city"),
        },
        "appointment": appointment,
        "visit_reason": None,
        "patient_message": None,
    }


def build_doctor_confirmation_message(
    booking_state: dict,
) -> str:
    doctor = booking_state["doctor"]
    appointment = booking_state["appointment"]

    city = f", {doctor['city']}" if doctor.get("city") else ""

    message = (
        f"I found {doctor['name']} — "
        f"{doctor['specialization']} at "
        f"{doctor['hospital_name']}{city}."
    )

    if (
        appointment.get("date")
        and appointment.get("day")
        and appointment.get("time")
    ):
        message += (
            f"\n\nYour requested appointment time is "
            f"{appointment['day']}, "
            f"{appointment['date']} at "
            f"{appointment['time']}."
        )

    message += "\n\nWould you like to continue with this doctor?"
    return message


def build_appointment_summary(
    booking_state: dict,
) -> str:
    doctor = booking_state["doctor"]
    appointment = booking_state["appointment"]

    return (
        "Please confirm your appointment details:\n\n"
        f"Doctor: {doctor['name']}\n"
        f"Specialization: {doctor['specialization']}\n"
        f"Hospital: {doctor['hospital_name']}\n"
        f"City: {doctor.get('city') or 'Not specified'}\n"
        f"Date: {appointment.get('date') or 'Not specified'}\n"
        f"Day: {appointment.get('day') or 'Not specified'}\n"
        f"Time: {appointment.get('time') or 'Not specified'}\n"
        f"Reason: {booking_state.get('visit_reason') or 'Not provided'}\n"
        f"Additional note: "
        f"{booking_state.get('patient_message') or 'None'}\n\n"
        "Would you like me to confirm and send this "
        "appointment request to the doctor?"
    )


# =========================================================
# SEARCH RESULT -> PERSISTABLE BOOKING STATE
# =========================================================

def apply_doctor_search_result(
    ai_response: dict,
    query: str,
    doctors: list[dict],
    workflow: dict | None = None,
    user_message: str = "",
) -> dict:
    workflow = workflow or {}

    if not doctors:
        ai_response["success"] = True
        ai_response["message"] = create_doctor_message(doctors)
        ai_response["metadata"] = {
            "booking_step": "doctor_search",
            "doctor_name": query,
            "doctor_options": [],
        }
        ai_response["workflow"] = {
            "step": "doctor_search",
            "query": query,
            "doctor_options": [],
            "selected_doctor_id": None,
        }
        ai_response["requires_confirmation"] = False
        ai_response["booking_state"] = None
        return ai_response

    if len(doctors) > 1:
        ai_response["success"] = True
        ai_response["message"] = create_doctor_message(doctors)
        ai_response["metadata"] = {
            "booking_step": "doctor_selection",
            "doctor_name": query,
            "doctor_options": doctors,
        }
        ai_response["workflow"] = {
            "step": "doctor_selection",
            "query": query,
            "doctor_options": doctors,
            "selected_doctor_id": None,
            "date_expression": workflow.get("date_expression"),
            "time": workflow.get("time"),
        }
        ai_response["requires_confirmation"] = False

        # We persist the search options as state so the next message
        # can be handled deterministically by the backend.
        ai_response["booking_state"] = {
            "step": "doctor_selection",
            "doctor_options": doctors,
            "query": query,
            "appointment": {
                "date_expression": normalize_date_expression(
                    workflow.get("date_expression")
                    or extract_date_expression(user_message)
                ) or None,
                "date": None,
                "day": None,
                "time": normalize_time(
                    workflow.get("time")
                    or extract_time_from_text(user_message)
                ),
                "requested_start_at": None,
                "duration_minutes": workflow.get(
                    "duration_minutes",
                    30,
                ),
            },
            "visit_reason": None,
            "patient_message": None,
        }
        return ai_response

    doctor = doctors[0]

    booking_state = create_booking_state(
        doctor=doctor,
        workflow=workflow,
        user_message=user_message,
    )

    appointment = booking_state["appointment"]

    ai_response["success"] = True
    ai_response["message"] = build_doctor_confirmation_message(
        booking_state
    )
    ai_response["metadata"] = {
        "booking_step": "doctor_confirmation",
        "doctor_name": doctor["doctor_name"],
        "specialization": doctor["specialization"],
        "hospital_id": doctor["hospital_id"],
        "hospital_name": doctor["hospital_name"],
        "city": doctor.get("city"),
        "date_expression": appointment.get("date_expression"),
        "resolved_date": appointment.get("date"),
        "day": appointment.get("day"),
        "time": appointment.get("time"),
    }
    ai_response["workflow"] = {
        "step": "doctor_confirmation",
        "query": query,
        "selected_doctor_id": doctor["doctor_id"],
        "date_expression": appointment.get("date_expression"),
        "time": appointment.get("time"),
    }
    ai_response["requires_confirmation"] = False

    # THIS IS THE CRITICAL FIX.
    # chat.py will persist this booking_state in Conversation.extra_data.
    ai_response["booking_state"] = booking_state

    return ai_response


# =========================================================
# ACTIVE BOOKING STATE HANDLER
# =========================================================

async def handle_existing_appointment_state(
    db,
    user_id: int,
    user_message: str,
    booking_state: dict,
    ai_response: dict,
):
    step = booking_state.get("step")

    print("ACTIVE BOOKING STEP:", step)
    print("ACTIVE BOOKING STATE:", booking_state)

    # -----------------------------------------------------
    # DOCTOR SELECTION
    # -----------------------------------------------------

    if step == "doctor_selection":
        options = booking_state.get("doctor_options") or []

        if not options:
            return None

        selected_doctor = None
        text = user_message.strip()

        if text.isdigit():
            index = int(text) - 1
            if 0 <= index < len(options):
                selected_doctor = options[index]

        if selected_doctor is None:
            lowered = text.lower()
            for doctor in options:
                if (
                    lowered == doctor["doctor_name"].lower()
                    or lowered in doctor["doctor_name"].lower()
                ):
                    selected_doctor = doctor
                    break

        if selected_doctor is None:
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": create_doctor_message(options),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "doctor_selection",
                    "doctor_options": options,
                },
                "workflow": {
                    "step": "doctor_selection",
                },
                "booking_state": booking_state,
            }

        appointment = booking_state.get("appointment") or {}

        selected_state = create_booking_state(
            doctor=selected_doctor,
            workflow={
                "date_expression": appointment.get(
                    "date_expression"
                ),
                "time": appointment.get("time"),
                "duration_minutes": appointment.get(
                    "duration_minutes",
                    30,
                ),
            },
        )

        booking_state = selected_state

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": build_doctor_confirmation_message(
                booking_state
            ),
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": False,
            "metadata": {
                "booking_step": "doctor_confirmation"
            },
            "workflow": {
                "step": "doctor_confirmation"
            },
            "booking_state": booking_state,
        }

    # -----------------------------------------------------
    # DOCTOR CONFIRMATION
    # -----------------------------------------------------

    if step == "doctor_confirmation":
        if is_yes(user_message):
            appointment = booking_state.get("appointment") or {}

            if (
                appointment.get("date")
                and appointment.get("time")
                and appointment.get("requested_start_at")
            ):
                booking_state["step"] = "visit_reason"

                return {
                    "success": True,
                    "intent": "appointment_booking",
                    "message": "What is the reason for your visit?",
                    "requires_location": False,
                    "requires_business_name": False,
                    "requires_confirmation": False,
                    "metadata": {
                        "booking_step": "visit_reason"
                    },
                    "workflow": {
                        "step": "visit_reason"
                    },
                    "booking_state": booking_state,
                }

            booking_state["step"] = "date_time"

            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "What date and time would you like "
                    "for the appointment?"
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "date_time"
                },
                "workflow": {
                    "step": "date_time"
                },
                "booking_state": booking_state,
            }

        if is_no(user_message):
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "Okay, I won't continue with this "
                    "appointment request."
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "cancelled"
                },
                "workflow": {
                    "step": "cancelled"
                },
                "booking_state": None,
            }

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": (
                "Please reply Yes if you would like "
                "to continue with this doctor, or No "
                "to cancel."
            ),
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": False,
            "metadata": {
                "booking_step": "doctor_confirmation"
            },
            "workflow": {
                "step": "doctor_confirmation"
            },
            "booking_state": booking_state,
        }

    # -----------------------------------------------------
    # DATE / TIME
    # -----------------------------------------------------

    if step == "date_time":
        appointment = booking_state.setdefault(
            "appointment",
            {},
        )

        date_expression = extract_date_expression(
            user_message
        )

        time_text = extract_time_from_text(
            user_message
        )

        if date_expression:
            appointment["date_expression"] = date_expression

        if time_text:
            appointment["time"] = time_text

        date_expression = appointment.get(
            "date_expression"
        )
        time_text = appointment.get("time")

        if not date_expression:
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": "What date would you like for the appointment?",
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "date_time"
                },
                "workflow": {
                    "step": "date_time"
                },
                "booking_state": booking_state,
            }

        appointment_date = resolve_relative_date(
            date_expression
        )

        if not appointment_date:
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "I couldn't determine that date. "
                    "Please provide a date such as "
                    "tomorrow or day after tomorrow."
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "date_time"
                },
                "workflow": {
                    "step": "date_time",
                },
                "booking_state": booking_state,
            }

        if not time_text:
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": "What time would you like for the appointment?",
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "date_time",
                    "resolved_date": appointment_date.isoformat(),
                },
                "workflow": {
                    "step": "date_time"
                },
                "booking_state": booking_state,
            }

        requested_start_at = build_requested_start_at(
            appointment_date,
            time_text,
        )

        if not requested_start_at:
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "I couldn't understand that time. "
                    "Please provide a time such as 6:30 PM."
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "date_time"
                },
                "workflow": {
                    "step": "date_time"
                },
                "booking_state": booking_state,
            }

        appointment["date"] = appointment_date.strftime(
            "%d/%m/%Y"
        )
        appointment["day"] = appointment_date.strftime("%A")
        appointment["time"] = normalize_time(time_text)
        appointment["requested_start_at"] = (
            requested_start_at.isoformat()
        )
        appointment.setdefault("duration_minutes", 30)

        booking_state["step"] = "visit_reason"

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": "What is the reason for your visit?",
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": False,
            "metadata": {
                "booking_step": "visit_reason",
                "resolved_date": appointment["date"],
                "day": appointment["day"],
                "time": appointment["time"],
            },
            "workflow": {
                "step": "visit_reason"
            },
            "booking_state": booking_state,
        }

    # -----------------------------------------------------
    # VISIT REASON
    # -----------------------------------------------------

    if step == "visit_reason":
        reason = user_message.strip()

        if is_skip(reason):
            booking_state["visit_reason"] = None
        else:
            booking_state["visit_reason"] = reason

        booking_state["step"] = "patient_note"

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": (
                "Do you have any additional note or "
                "message you would like me to pass "
                "to the doctor?"
            ),
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": False,
            "metadata": {
                "booking_step": "patient_note",
                "visit_reason": booking_state.get(
                    "visit_reason"
                ),
            },
            "workflow": {
                "step": "patient_note"
            },
            "booking_state": booking_state,
        }

    # -----------------------------------------------------
    # PATIENT NOTE
    # -----------------------------------------------------

    if step == "patient_note":
        booking_state["patient_message"] = (
            None
            if is_skip(user_message)
            else user_message.strip()
        )

        booking_state["step"] = "confirmation"

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": build_appointment_summary(
                booking_state
            ),
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": True,
            "metadata": {
                "booking_step": "confirmation"
            },
            "workflow": {
                "step": "confirmation"
            },
            "booking_state": booking_state,
        }

    # -----------------------------------------------------
    # FINAL CONFIRMATION
    # -----------------------------------------------------

    if step == "confirmation":
        if is_yes(user_message):
            booking_state["step"] = "completed"

            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "Your appointment request is being "
                    "sent to the doctor."
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {},
                "workflow": {
                    "step": "completed",
                    "action": "create_appointment_request",
                },
                "booking_state": booking_state,
            }

        if is_no(user_message):
            return {
                "success": True,
                "intent": "appointment_booking",
                "message": (
                    "Okay, I won't submit the "
                    "appointment request."
                ),
                "requires_location": False,
                "requires_business_name": False,
                "requires_confirmation": False,
                "metadata": {
                    "booking_step": "cancelled"
                },
                "workflow": {
                    "step": "cancelled"
                },
                "booking_state": None,
            }

        return {
            "success": True,
            "intent": "appointment_booking",
            "message": build_appointment_summary(
                booking_state
            ),
            "requires_location": False,
            "requires_business_name": False,
            "requires_confirmation": True,
            "metadata": {
                "booking_step": "confirmation"
            },
            "workflow": {
                "step": "confirmation"
            },
            "booking_state": booking_state,
        }

    return None


# =========================================================
# MAIN ROUTER
# =========================================================

async def route_workflow(
    ai_response: dict,
    db,
    user_message: str,
    user_id: int,
    booking_state: dict | None = None,
) -> dict:

    print("\n========== ROUTE WORKFLOW ==========")
    print("USER MESSAGE:", user_message)
    print("BOOKING STATE:", booking_state)
    print("AI RESPONSE:", ai_response)

    # CRITICAL:
    # Existing state MUST be processed before LLM intent/step.
    # Therefore "yes" cannot start a new appointment flow.
    if booking_state:
        result = await handle_existing_appointment_state(
            db=db,
            user_id=user_id,
            user_message=user_message,
            booking_state=booking_state,
            ai_response=ai_response,
        )

        if result is not None:
            return result

    intent = ai_response.get("intent")
    workflow = ai_response.get("workflow") or {}
    step = workflow.get("step")

    # =====================================================
    # MEDICINE
    # =====================================================

    if intent == "medicine_order":
        return await handle_medicine_workflow(ai_response)

    # =====================================================
    # APPOINTMENT
    # =====================================================

    if intent == "appointment_booking":

        # ---------------------------------------------
        # SPECIALIST SEARCH
        # ---------------------------------------------

        if step == "specialist_search":
            query = (workflow.get("query") or "").strip()

            if not query:
                ai_response["message"] = (
                    "Which medical specialization "
                    "would you like to book an appointment for?"
                )
                return ai_response

            doctors = await search_doctors_by_specialization(
                db=db,
                specialization=query,
            )

            return apply_doctor_search_result(
                ai_response=ai_response,
                query=query,
                doctors=doctors,
                workflow=workflow,
                user_message=user_message,
            )

        # ---------------------------------------------
        # DOCTOR SEARCH
        # ---------------------------------------------

        # doctor_found is also handled here for backward
        # compatibility with an older LLM response.
        if step in {"doctor_search", "doctor_found"}:

            query = (
                workflow.get("query")
                or extract_doctor_query(user_message)
            ).strip()

            if not query:
                ai_response["message"] = (
                    "Which doctor's name would you like "
                    "to book an appointment with?"
                )
                ai_response["workflow"] = {
                    "step": "doctor_search"
                }
                return ai_response

            doctors = await search_doctors(
                db=db,
                query=query,
            )

            if not doctors:
                doctors = (
                    await search_doctors_by_specialization(
                        db=db,
                        specialization=query,
                    )
                )

            return apply_doctor_search_result(
                ai_response=ai_response,
                query=query,
                doctors=doctors,
                workflow=workflow,
                user_message=user_message,
            )

        # ---------------------------------------------
        # DOCTOR SELECTION WITHOUT SAVED STATE
        # ---------------------------------------------

        if step == "doctor_selection":
            options = workflow.get("doctor_options") or []
            query = (workflow.get("query") or "").strip()

            if not options and query:
                options = await search_doctors(
                    db=db,
                    query=query,
                )

            if not options:
                query = extract_doctor_query(user_message)

                if query:
                    options = await search_doctors(
                        db=db,
                        query=query,
                    )

            if not options:
                ai_response["message"] = (
                    "Please provide the doctor's name "
                    "you would like to book."
                )
                ai_response["workflow"] = {
                    "step": "doctor_search"
                }
                return ai_response

            # If this is a real selection, persist options.
            state = {
                "step": "doctor_selection",
                "doctor_options": options,
                "query": query,
                "appointment": {
                    "date_expression": (
                        workflow.get("date_expression")
                        or extract_date_expression(user_message)
                        or None
                    ),
                    "date": None,
                    "day": None,
                    "time": normalize_time(
                        workflow.get("time")
                        or extract_time_from_text(user_message)
                    ),
                    "requested_start_at": None,
                    "duration_minutes": workflow.get(
                        "duration_minutes",
                        30,
                    ),
                },
                "visit_reason": None,
                "patient_message": None,
            }

            # Let the state handler process numeric/name selection.
            return await handle_existing_appointment_state(
                db=db,
                user_id=user_id,
                user_message=user_message,
                booking_state=state,
                ai_response=ai_response,
            )

        # ---------------------------------------------
        # DATE/TIME WITHOUT AN ACTIVE STATE
        # ---------------------------------------------

        if step == "date_time":
            date_expression = normalize_date_expression(
                workflow.get("date_expression")
                or extract_date_expression(user_message)
            )
            time_text = normalize_time(
                workflow.get("time")
                or extract_time_from_text(user_message)
            )

            if not date_expression:
                ai_response["message"] = (
                    "What date would you like for the appointment?"
                )
                return ai_response

            appointment_date = resolve_relative_date(
                date_expression
            )

            if not appointment_date:
                ai_response["message"] = (
                    "I couldn't determine that date. "
                    "Please provide a date such as tomorrow "
                    "or day after tomorrow."
                )
                return ai_response

            if not time_text:
                ai_response["message"] = (
                    "What time would you like for the appointment?"
                )
                return ai_response

            ai_response["success"] = True
            ai_response["message"] = (
                f"The requested appointment time is "
                f"{appointment_date.strftime('%A, %d/%m/%Y')} "
                f"at {time_text}."
            )
            ai_response["metadata"] = {
                "booking_step": "date_time",
                "date_expression": date_expression,
                "resolved_date": appointment_date.isoformat(),
                "time": time_text,
            }
            ai_response["workflow"] = {
                "step": "date_time",
                "date_expression": date_expression,
                "resolved_date": appointment_date.isoformat(),
                "time": time_text,
            }
            return ai_response

    return ai_response
