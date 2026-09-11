import os

import httpx
from dotenv import load_dotenv


load_dotenv()


MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_WIDGET_ID = os.getenv("MSG91_WIDGET_ID")

MSG91_SEND_OTP_URL = (
    "https://api.msg91.com/api/v5/widget/sendOtp"
)

MSG91_VERIFY_OTP_URL = (
    "https://api.msg91.com/api/v5/widget/verifyOtp"
)


async def send_otp(
    mobile: str
) -> dict:

    if not MSG91_AUTH_KEY:
        raise RuntimeError("MSG91_AUTH_KEY is not configured")

    if not MSG91_WIDGET_ID:
        raise RuntimeError("MSG91_WIDGET_ID is not configured")

    payload = {
        "widgetId": MSG91_WIDGET_ID,
        "identifier": mobile,
    }

    headers = {
        "authkey": MSG91_AUTH_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            MSG91_SEND_OTP_URL,
            json=payload,
            headers=headers,
            timeout=15.0,
        )

    response.raise_for_status()

    return response.json()