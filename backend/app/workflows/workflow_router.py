from app.workflows.medicine_workflow import (
    handle_medicine_workflow
)


async def route_workflow(
    ai_response: dict
):

    intent = ai_response.get("intent")

    if intent == "medicine_order":

        return await handle_medicine_workflow(
            ai_response
        )

    return ai_response