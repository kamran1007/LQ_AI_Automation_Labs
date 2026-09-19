import re
from difflib import SequenceMatcher

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.doctor import Doctor
from app.models.hospital import Hospital


# =========================================================
# NORMALIZATION
# =========================================================

def normalize_doctor_query(query: str) -> str:
    """
    Normalize a doctor search query.

    Examples:
        "Dr. Sharma"       -> "sharma"
        "Dr Sharma"        -> "sharma"
        "DR. Sneha"        -> "sneha"
        "  Dr. Amit  "     -> "amit"
    """

    if not query:
        return ""

    query = query.strip().lower()

    # Remove doctor title only from the beginning.
    query = re.sub(r"^dr\.?\s*", "", query)

    # Normalize whitespace.
    query = " ".join(query.split())

    return query


# =========================================================
# STRING SIMILARITY
# =========================================================

def similarity(a: str, b: str) -> float:
    """
    Return similarity between two strings.

    Example:
        sheha vs sneha -> high similarity
        sheha vs rajesh -> low similarity
    """

    return SequenceMatcher(
        None,
        a.lower(),
        b.lower(),
    ).ratio()


# =========================================================
# BUILD DOCTOR RESPONSE
# =========================================================

def doctor_to_dict(
    doctor: Doctor,
    hospital: Hospital,
) -> dict:

    return {
        "doctor_id": doctor.id,
        "doctor_name": doctor.name,
        "specialization": doctor.specialization,
        "hospital_id": hospital.id,
        "hospital_name": hospital.name,
        "city": getattr(hospital, "city", None),
    }


# =========================================================
# DOCTOR SEARCH
# =========================================================

async def search_doctors(
    db: AsyncSession,
    query: str,
) -> list[dict]:

    search_text = normalize_doctor_query(query)

    print("\n========== DOCTOR SEARCH ==========")
    print("RAW QUERY:", repr(query))
    print("NORMALIZED QUERY:", repr(search_text))

    if not search_text:
        print("EMPTY DOCTOR QUERY")
        return []

    # =====================================================
    # LOAD ACTIVE DOCTORS
    # =====================================================

    statement = (
        select(Doctor, Hospital)
        .join(
            Hospital,
            Doctor.hospital_id == Hospital.id,
        )
        .where(
            Doctor.is_active.is_(True),
            Hospital.is_active.is_(True),
        )
        .order_by(Doctor.name.asc())
    )

    result = await db.execute(statement)

    rows = result.all()

    print("ACTIVE DOCTOR COUNT:", len(rows))

    # =====================================================
    # 1. EXACT / PARTIAL SEARCH
    # =====================================================
    #
    # This handles:
    #
    #   Sneha
    #       -> Dr. Sneha Sharma
    #       -> Dr. Sneha Rao
    #
    #   Sharma
    #       -> Dr. Amit Sharma
    #       -> Dr. Sneha Sharma
    #
    #   Amit Sharma
    #       -> Dr. Amit Sharma
    #
    # =====================================================

    exact_matches = []

    for doctor, hospital in rows:

        normalized_name = re.sub(
            r"^dr\.?\s*",
            "",
            doctor.name.lower(),
        ).strip()

        if search_text in normalized_name:

            exact_matches.append(
                doctor_to_dict(
                    doctor,
                    hospital,
                )
            )

    print(
        "EXACT/PARTIAL MATCH COUNT:",
        len(exact_matches),
    )

    for doctor in exact_matches:
        print(
            "EXACT MATCH:",
            doctor["doctor_id"],
            doctor["doctor_name"],
            "|",
            doctor["hospital_name"],
        )

    # Exact/partial matches always win.
    if exact_matches:

        print(
            "RETURNING EXACT/PARTIAL MATCHES"
        )

        return exact_matches[:20]

    # =====================================================
    # 2. FUZZY SEARCH
    # =====================================================
    #
    # Only used when exact/partial search found nothing.
    #
    # Example:
    #
    #   sheha
    #      ↓
    #   sneha
    #
    # =====================================================

    fuzzy_matches = []

    for doctor, hospital in rows:

        normalized_name = re.sub(
            r"^dr\.?\s*",
            "",
            doctor.name.lower(),
        ).strip()

        name_tokens = normalized_name.split()

        if not name_tokens:
            continue

        best_score = 0.0

        for token in name_tokens:

            # Ignore very short tokens.
            if len(token) < 4:
                continue

            score = similarity(
                search_text,
                token,
            )

            if score > best_score:
                best_score = score

        print(
            "FUZZY CHECK:",
            doctor.name,
            "->",
            round(best_score, 3),
        )

        # Conservative threshold.
        #
        # "sheha" vs "sneha" -> ~0.8
        # "sheha" vs "neha"  -> lower
        #
        if best_score >= 0.75:

            fuzzy_matches.append(
                (
                    best_score,
                    doctor_to_dict(
                        doctor,
                        hospital,
                    ),
                )
            )

    # Highest similarity first.
    fuzzy_matches.sort(
        key=lambda item: (
            -item[0],
            item[1]["doctor_name"].lower(),
        )
    )

    doctors = [
        doctor
        for score, doctor in fuzzy_matches[:20]
    ]

    print(
        "FUZZY MATCH COUNT:",
        len(doctors),
    )

    for doctor in doctors:
        print(
            "FUZZY MATCH:",
            doctor["doctor_id"],
            doctor["doctor_name"],
        )

    print("========== DOCTOR SEARCH END ==========\n")

    return doctors