async def handle_medicine_workflow(
    ai_response: dict
):

    metadata = ai_response.get(
        "metadata",
        {}
    )

    medicine_name = metadata.get(
        "medicine_name"
    )

    if medicine_name:

        ai_response["workflow"] = {
            "step": "collect_location",
            "medicine_name": medicine_name,
            "status": "awaiting_location"
        }

    return ai_response