import os

import httpx


MSG91_VERIFY_ACCESS_TOKEN_URL = (
    "https://control.msg91.com/api/v5/widget/verifyAccessToken"
)


async def verify_msg91_access_token(
    access_token: str,
) -> dict:

    auth_key = os.getenv("MSG91_AUTH_KEY")

    if not auth_key:
        raise RuntimeError(
            "MSG91_AUTH_KEY is not configured"
        )

    headers = {
        "authkey": auth_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "access-token": access_token,
    }

    async with httpx.AsyncClient(
        timeout=15.0
    ) as client:

        response = await client.post(
            MSG91_VERIFY_ACCESS_TOKEN_URL,
            headers=headers,
            json=payload,
        )

    try:
        data = response.json()

    except ValueError as exc:
        raise ValueError(
            "MSG91 returned an invalid JSON response"
        ) from exc

    if response.status_code >= 400:
        raise ValueError(
            f"MSG91 verification failed: "
            f"{response.status_code} - {data}"
        )

    return data