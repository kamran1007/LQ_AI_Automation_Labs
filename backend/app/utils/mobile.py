import re


def normalize_indian_mobile(mobile: str) -> str:
    """
    Normalize an Indian mobile number to:
        91XXXXXXXXXX

    Accepted formats:
        8421205672
        918421205672
        +918421205672
        +91 8421205672
        0918421205672
    """

    if not mobile:
        raise ValueError("Mobile number is required.")

    # Remove spaces, +, -, etc.
    digits = re.sub(r"\D", "", mobile)

    # 0XXXXXXXXXX -> XXXXXXXXXX
    if len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]

    # 91XXXXXXXXXX
    if len(digits) == 12 and digits.startswith("91"):
        national_number = digits[2:]

    # XXXXXXXXXX
    elif len(digits) == 10:
        national_number = digits

    else:
        raise ValueError("Invalid Indian mobile number.")

    # Indian mobile numbers start with 6, 7, 8 or 9
    if not re.fullmatch(r"[6-9]\d{9}", national_number):
        raise ValueError("Invalid Indian mobile number.")

    return f"91{national_number}"