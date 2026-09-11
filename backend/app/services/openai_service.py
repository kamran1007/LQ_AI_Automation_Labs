import json
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """
You are LightningQ AI Automation Assistant.

You MUST ALWAYS respond ONLY in valid JSON format.

Supported intents:
- appointment_booking
- medicine_order
- nearby_search
- quotation_request
- invoice_request
- support_query
- general_query

Response format:

{
  "success": true,
  "intent": "medicine_order",
  "message": "Please provide medicine name and location.",
  "requires_location": true,
  "requires_business_name": false,
  "requires_confirmation": false,
  "metadata": {}
}

Rules:
- Always return valid JSON
- Never return plain text
- Keep responses concise
- Detect business intent carefully
"""


def ask_ai(
    message: str,
    history: list | None = None
):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ]

    if history:

        for convo in history:

            messages.append({
                "role": "user",
                "content": convo.message
            })

            messages.append({
                "role": "assistant",
                "content": convo.ai_response
            })

    messages.append({
        "role": "user",
        "content": message
    })

    response = client.chat.completions.create(
        model="gpt-5.4-mini",

        response_format={
            "type": "json_object"
        },

        messages=messages
    )

    content = response.choices[0].message.content

    return json.loads(content)
