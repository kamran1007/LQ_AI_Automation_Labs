import re

from app.services.doctor_search_service import search_doctors
from app.workflows.medicine_workflow import handle_medicine_workflow


# =========================================================
# DOCTOR MESSAGE
# =========================================================

def create_doctor_message(
    doctors: list[dict],
) -> str:

    if not doctors:

        return (
            "I could not find an active doctor matching "
            "your search. Please provide another doctor's "
            "name, hospital name, or medical specialization."
        )

    # -----------------------------------------------------
    # ONE DOCTOR
    # -----------------------------------------------------

    if len(doctors) == 1:

        doctor = doctors[0]

        city_text = ""

        if doctor.get("city"):
            city_text = f", {doctor['city']}"

        return (
            f"I found {doctor['doctor_name']} — "
            f"{doctor['specialization']} at "
            f"{doctor['hospital_name']}"
            f"{city_text}. "
            "Would you like to continue with this doctor?"
        )

    # -----------------------------------------------------
    # MULTIPLE DOCTORS
    # -----------------------------------------------------

    lines = [
        "I found multiple doctors matching your search. "
        "Please select the doctor you would like to consult:"
    ]

    for index, doctor in enumerate(
        doctors,
        start=1,
    ):

        city_text = ""

        if doctor.get("city"):
            city_text = f", {doctor['city']}"

        lines.append(
            f"{index}. "
            f"{doctor['doctor_name']} — "
            f"{doctor['specialization']} — "
            f"{doctor['hospital_name']}"
            f"{city_text}"
        )

    return "\n".join(lines)


# =========================================================
# EXTRACT DOCTOR QUERY FROM ORIGINAL USER MESSAGE
# =========================================================

def extract_doctor_query(
    message: str,
) -> str:
    """
    Recover the doctor name from the original user message.

    Examples:

        book an appointment with dr. Sneha
            -> Sneha

        book appointment with Dr. Sharma
            -> Sharma

        I want to see Dr. Amit Sharma
            -> Amit Sharma

        appointment with dr Rahul Verma
            -> Rahul Verma
    """

    if not message:
        return ""

    text = message.strip()

    # -----------------------------------------------------
    # Doctor title
    # -----------------------------------------------------

    match = re.search(
        r"\bdr\.?\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        text,
        re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        # Remove trailing booking words if present.
        query = re.split(
            r"\b(?:for|at|on|tomorrow|today|please)\b",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        return query

    # -----------------------------------------------------
    # "doctor Sharma" style
    # -----------------------------------------------------

    match = re.search(
        r"\bdoctor\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})",
        text,
        re.IGNORECASE,
    )

    if match:

        query = match.group(1).strip()

        query = re.split(
            r"\b(?:for|at|on|tomorrow|today|please)\b",
            query,
            maxsplit=1,
            flags=re.IGNORECASE,
        )[0].strip()

        return query

    return ""


# =========================================================
# APPLY DOCTOR SEARCH RESULT
# =========================================================

def apply_doctor_search_result(
    ai_response: dict,
    query: str,
    doctors: list[dict],
) -> dict:

    # -----------------------------------------------------
    # NO DOCTOR
    # -----------------------------------------------------

    if not doctors:

        ai_response["message"] = create_doctor_message(
            doctors
        )

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

        return ai_response

    # -----------------------------------------------------
    # MULTIPLE DOCTORS
    # -----------------------------------------------------

    if len(doctors) > 1:

        ai_response["message"] = create_doctor_message(
            doctors
        )

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
        }

        ai_response["requires_confirmation"] = False

        return ai_response

    # -----------------------------------------------------
    # ONE DOCTOR
    # -----------------------------------------------------

    doctor = doctors[0]

    ai_response["message"] = create_doctor_message(
        doctors
    )

    ai_response["metadata"] = {
        "booking_step": "doctor_found",
        "doctor_name": doctor["doctor_name"],
        "specialization": doctor["specialization"],
        "hospital_id": doctor["hospital_id"],
        "hospital_name": doctor["hospital_name"],
        "city": doctor.get("city"),
        "doctor_options": doctors,
    }

    ai_response["workflow"] = {
        "step": "doctor_found",
        "query": query,
        "doctor_options": doctors,
        "selected_doctor_id": doctor["doctor_id"],
    }

    ai_response["requires_confirmation"] = False

    return ai_response


# =========================================================
# ROUTE WORKFLOW
# =========================================================

async def route_workflow(
    ai_response: dict,
    db,
    user_message: str,
) -> dict:

    print(
        "\n========== ROUTE WORKFLOW: START =========="
    )

    print("USER MESSAGE:")
    print(user_message)

    print("AI RESPONSE BEFORE ROUTING:")
    print(ai_response)

    intent = ai_response.get("intent")

    workflow = ai_response.get("workflow") or {}

    step = workflow.get("step")

    print("INTENT:", intent)
    print("WORKFLOW STEP:", step)
    print("WORKFLOW:", workflow)

    # =====================================================
    # MEDICINE WORKFLOW
    # =====================================================

    if intent == "medicine_order":

        result = await handle_medicine_workflow(
            ai_response
        )

        print("MEDICINE WORKFLOW RESULT:")
        print(result)

        print(
            "========== ROUTE WORKFLOW: END ==========\n"
        )

        return result

    # =====================================================
    # APPOINTMENT BOOKING
    # =====================================================

    if intent == "appointment_booking":

        # =================================================
        # CASE 1:
        # LLM CORRECTLY RETURNS doctor_search
        # =================================================

        if step == "doctor_search":

            query = (
                workflow.get("query") or ""
            ).strip()

            print(
                "DOCTOR SEARCH STEP"
            )

            print(
                "QUERY FROM LLM:",
                repr(query),
            )

            # -------------------------------------------------
            # If LLM forgot the query, recover from user message.
            # -------------------------------------------------

            if not query:

                query = extract_doctor_query(
                    user_message
                )

                print(
                    "RECOVERED QUERY FROM USER:",
                    repr(query),
                )

            # -------------------------------------------------
            # Search database
            # -------------------------------------------------

            if query:

                doctors = await search_doctors(
                    db=db,
                    query=query,
                )

                print(
                    "DOCTORS FOUND:",
                    len(doctors),
                )

                return apply_doctor_search_result(
                    ai_response=ai_response,
                    query=query,
                    doctors=doctors,
                )

            # No doctor query available.
            ai_response["message"] = (
                "Sure. Which doctor's name would "
                "you like to book an appointment with?"
            )

            ai_response["workflow"] = {
                "step": "initial",
                "selected_doctor_id": None,
            }

            ai_response["metadata"] = {
                "booking_step": "initial",
            }

            ai_response["requires_confirmation"] = False

            return ai_response

        # =================================================
        # CASE 2:
        # LLM INCORRECTLY RETURNS doctor_selection
        # ON INITIAL REQUEST
        # =================================================

        if step == "doctor_selection":

            print(
                "DOCTOR SELECTION STEP"
            )

            doctor_options = (
                workflow.get("doctor_options")
                or []
            )

            query = (
                workflow.get("query")
                or ""
            ).strip()

            print(
                "DOCTOR OPTIONS FROM LLM:",
                doctor_options,
            )

            print(
                "QUERY FROM LLM:",
                repr(query),
            )

            # -------------------------------------------------
            # CRITICAL FALLBACK
            #
            # If LLM gave doctor_selection without options,
            # check the ORIGINAL USER MESSAGE.
            # -------------------------------------------------

            if not doctor_options:

                if not query:

                    query = extract_doctor_query(
                        user_message
                    )

                    print(
                        "RECOVERED DOCTOR QUERY:",
                        repr(query),
                    )

                # ---------------------------------------------
                # We found a doctor query in the user's message.
                # This means this is actually a SEARCH.
                # ---------------------------------------------

                if query:

                    print(
                        "LLM RETURNED doctor_selection "
                        "FOR INITIAL SEARCH."
                    )

                    print(
                        "RECOVERING USING BACKEND SEARCH."
                    )

                    doctors = await search_doctors(
                        db=db,
                        query=query,
                    )

                    print(
                        "FALLBACK DOCTORS FOUND:",
                        len(doctors),
                    )

                    return apply_doctor_search_result(
                        ai_response=ai_response,
                        query=query,
                        doctors=doctors,
                    )

            # -------------------------------------------------
            # Existing doctor options.
            #
            # This is a REAL doctor selection step.
            # -------------------------------------------------

            if doctor_options:

                print(
                    "EXISTING DOCTOR OPTIONS FOUND."
                )

                # Keep the options from backend state.
                ai_response["metadata"] = {
                    "booking_step": "doctor_selection",
                    "doctor_options": doctor_options,
                }

                ai_response["workflow"] = {
                    "step": "doctor_selection",
                    "query": query or None,
                    "doctor_options": doctor_options,
                    "selected_doctor_id": workflow.get(
                        "selected_doctor_id"
                    ),
                }

                ai_response["requires_confirmation"] = False

                return ai_response

            # -------------------------------------------------
            # Nothing available.
            # -------------------------------------------------

            print(
                "WARNING: doctor_selection received "
                "without doctor_options or doctor query."
            )

            ai_response["message"] = (
                "Please provide the doctor's name "
                "you would like to book an appointment with."
            )

            ai_response["metadata"] = {
                "booking_step": "initial",
            }

            ai_response["workflow"] = {
                "step": "initial",
                "selected_doctor_id": None,
            }

            ai_response["requires_confirmation"] = False

            return ai_response

        # =================================================
        # CASE 3:
        # DOCTOR ALREADY FOUND
        # =================================================

        if step == "doctor_found":

            doctor_options = (
                workflow.get("doctor_options")
                or []
            )

            selected_doctor_id = workflow.get(
                "selected_doctor_id"
            )

            print(
                "DOCTOR FOUND STEP"
            )

            print(
                "SELECTED DOCTOR ID:",
                selected_doctor_id,
            )

            # Backend already found this doctor.
            # Preserve the state.
            if selected_doctor_id:

                return ai_response

        # =================================================
        # OTHER APPOINTMENT STEPS
        # =================================================
        #
        # date_time
        # visit_reason
        # patient_message
        # confirmation
        # confirmed
        #
        # These will pass through until their respective
        # backend workflow handlers are added.
        # =================================================

    # =====================================================
    # NO MATCHING WORKFLOW
    # =====================================================

    print(
        "NO MATCHING WORKFLOW"
    )

    print(
        "RETURNING ORIGINAL AI RESPONSE:"
    )

    print(ai_response)

    print(
        "========== ROUTE WORKFLOW: END ==========\n"
    )

    return ai_response