import base64
import hashlib
import hmac
import json
import os
import time
import secrets


REGISTRATION_TOKEN_TTL_SECONDS = 10 * 60


def _get_registration_secret() -> str:
    secret = os.getenv("AUTH_REGISTRATION_SECRET")

    if not secret:
        raise RuntimeError(
            "AUTH_REGISTRATION_SECRET is not configured"
        )

    return secret


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode().rstrip("=")


def _decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(
        value + padding
    )


def create_registration_token(mobile: str) -> str:
    secret = _get_registration_secret().encode()

    payload = {
        "mobile": mobile,
        "expires_at": int(time.time()) + REGISTRATION_TOKEN_TTL_SECONDS,
        "nonce": secrets.token_urlsafe(16),
    }

    payload_bytes = json.dumps(
        payload,
        separators=(",", ":"),
    ).encode()

    encoded_payload = _encode(payload_bytes)

    signature = hmac.new(
        secret,
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()

    encoded_signature = _encode(signature)

    return f"{encoded_payload}.{encoded_signature}"


def verify_registration_token(token: str) -> dict:
    if not token or "." not in token:
        raise ValueError(
            "Invalid registration token."
        )

    encoded_payload, encoded_signature = token.split(
        ".",
        1,
    )

    secret = _get_registration_secret().encode()

    expected_signature = hmac.new(
        secret,
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()

    try:
        actual_signature = _decode(
            encoded_signature
        )
    except Exception as exc:
        raise ValueError(
            "Invalid registration token."
        ) from exc

    if not hmac.compare_digest(
        actual_signature,
        expected_signature,
    ):
        raise ValueError(
            "Invalid registration token."
        )

    try:
        payload = json.loads(
            _decode(encoded_payload)
        )
    except Exception as exc:
        raise ValueError(
            "Invalid registration token."
        ) from exc

    expires_at = payload.get("expires_at")
    mobile = payload.get("mobile")

    if not mobile or not expires_at:
        raise ValueError(
            "Invalid registration token."
        )

    if int(time.time()) >= int(expires_at):
        raise ValueError(
            "Registration session has expired. Please verify your mobile number again."
        )

    return payload