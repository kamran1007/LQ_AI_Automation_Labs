from datetime import datetime, timedelta
import re
from difflib import SequenceMatcher


def normalize_date_expression(text: str) -> str | None:
    if not text:
        return None

    text = " ".join(text.lower().strip().split())

    # Exact/common expressions first
    if "day after tomorrow" in text:
        return "day after tomorrow"

    if "tomorrow" in text:
        return "tomorrow"

    if re.search(r"\btoday\b", text):
        return "today"

    # Common typo variations
    typo_map = {
        "tommorow": "tomorrow",
        "tommow": "tomorrow",
        "tommowow": "tomorrow",
        "tomorow": "tomorrow",
        "tomarrow": "tomorrow",
        "tmorrow": "tomorrow",
        "tommorrow": "tomorrow",
    }

    for typo, correct in typo_map.items():
        if typo in text:
            return correct

    return None


def resolve_relative_date(
    text: str,
    now: datetime | None = None,
):
    if not text:
        return None

    if now is None:
        now = datetime.now().astimezone()

    expression = normalize_date_expression(text)

    if expression == "day after tomorrow":
        return now.date() + timedelta(days=2)

    if expression == "tomorrow":
        return now.date() + timedelta(days=1)

    if expression == "today":
        return now.date()

    return None


def format_appointment_datetime(
    appointment_datetime: datetime,
) -> str:
    return appointment_datetime.strftime(
        "%A, %d/%m/%Y at %I:%M %p"
    )