import re
from datetime import datetime


def parse_date(date_text):
    if not date_text:
        return None

    value = date_text.strip()
    value = value.replace("-", "/")
    value = value.replace(".", "/")

    formats = ["%d/%m/%Y", "%d/%m/%y"]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def normalize_date(date_text):
    if not date_text:
        return ""

    value = date_text.strip()
    value = value.replace("-", "/")
    value = value.replace(".", "/")

    match = re.search(
        r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b",
        value
    )

    if not match:
        return ""

    day = int(match.group(1))
    month = int(match.group(2))
    year = int(match.group(3))

    try:
        parsed = datetime(year, month, day)
    except ValueError:
        return ""

    return parsed.strftime("%d/%m/%Y")


def validate_licence_number(licence_number):
    field = "licence_number"

    if not licence_number:
        return {
            "field": field,
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Licence number could not be extracted "
                "from the document."
            )
        }

    value = licence_number.strip().upper()

    compact = re.sub(
        r"[^A-Z0-9]",
        "",
        value
    )

    if len(compact) < 6:
        return {
            "field": field,
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Extracted licence number is too short "
                "for reliable validation."
            )
        }

    # -------------------------------------------------
    # MASKED / DEMO LICENCE NUMBER
    # Example: MHXX XXXX XXXX
    # -------------------------------------------------
    masked_pattern = re.sub(
        r"[^A-Z0-9X]",
        "",
        value
    )

    if (
        "XX" in masked_pattern
        and not re.search(r"\d", compact)
    ):
        return {
            "field": field,
            "valid": True,
            "status": "PASS",
            "severity": "LOW",
            "message": (
                "Licence number appears to be a masked/demo "
                "value. Structural validation is limited."
            )
        }

    # -------------------------------------------------
    # INDIAN STATE / UT CODES
    # -------------------------------------------------
    state_code = compact[:2]

    valid_state_codes = {
        "AP", "AR", "AS", "BR", "CG",
        "CH", "DD", "DL", "DN", "GA",
        "GJ", "HP", "HR", "JH", "JK",
        "KA", "KL", "LA", "LD", "MH",
        "ML", "MN", "MP", "MZ", "NL",
        "OD", "PB", "PY", "RJ", "SK",
        "TN", "TR", "TS", "UK", "UP",
        "WB"
    }

    if state_code not in valid_state_codes:
        return {
            "field": field,
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Licence number does not begin with "
                "a recognized Indian state or UT code."
            )
        }

    has_letter = bool(
        re.search(r"[A-Z]", compact)
    )

    has_number = bool(
        re.search(r"\d", compact)
    )

    if not has_letter or not has_number:
        return {
            "field": field,
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Licence number does not contain the "
                "expected combination of letters and numbers."
            )
        }

    return {
        "field": field,
        "valid": True,
        "status": "PASS",
        "severity": "LOW",
        "message": (
            "Licence number has a valid state-code "
            "and alphanumeric structure."
        )
    }


def validate_dates(dob, issue_date, valid_until):
    results = []

    # -------------------------
    # DATE OF BIRTH
    # -------------------------
    if not dob:
        results.append({
            "field": "date_of_birth",
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": "Date of birth could not be extracted."
        })
    else:
        dob_date = parse_date(dob)

        if dob_date is None:
            results.append({
                "field": "date_of_birth",
                "valid": False,
                "status": "REVIEW",
                "severity": "MEDIUM",
                "message": (
                    "Date of birth has an invalid date format."
                )
            })
        else:
            current_year = datetime.now().year

            if dob_date.year > current_year:
                results.append({
                    "field": "date_of_birth",
                    "valid": False,
                    "status": "REVIEW",
                    "severity": "MEDIUM",
                    "message": "Date of birth is in the future."
                })
            else:
                results.append({
                    "field": "date_of_birth",
                    "valid": True,
                    "status": "PASS",
                    "severity": "LOW",
                    "message": "date_of_birth has a valid date."
                })

    # -------------------------
    # ISSUE DATE
    # -------------------------
    if not issue_date:
        results.append({
            "field": "issue_date",
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Licence issue date could not be extracted."
            )
        })
    else:
        issue = parse_date(issue_date)

        if issue is None:
            results.append({
                "field": "issue_date",
                "valid": False,
                "status": "REVIEW",
                "severity": "MEDIUM",
                "message": (
                    "Issue date has an invalid date format."
                )
            })
        else:
            results.append({
                "field": "issue_date",
                "valid": True,
                "status": "PASS",
                "severity": "LOW",
                "message": "issue_date has a valid date."
            })

    # -------------------------
    # VALID UNTIL
    # -------------------------
    if not valid_until:
        results.append({
            "field": "valid_until",
            "valid": False,
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": (
                "Licence validity date could not be extracted."
            )
        })
    else:
        valid_date = parse_date(valid_until)

        if valid_date is None:
            results.append({
                "field": "valid_until",
                "valid": False,
                "status": "REVIEW",
                "severity": "MEDIUM",
                "message": (
                    "Validity date has an invalid date format."
                )
            })
        else:
            results.append({
                "field": "valid_until",
                "valid": True,
                "status": "PASS",
                "severity": "LOW",
                "message": "valid_until has a valid date."
            })

    # -------------------------
    # DATE CONSISTENCY
    # -------------------------
    dob_date = parse_date(dob)
    issue = parse_date(issue_date)
    valid_date = parse_date(valid_until)

    consistency_messages = []

    if dob_date and issue:
        if dob_date >= issue:
            consistency_messages.append(
                "Date of birth is not earlier than "
                "the licence issue date."
            )

    if issue and valid_date:
        if valid_date <= issue:
            consistency_messages.append(
                "Licence validity date is not later "
                "than the issue date."
            )

    if dob_date and valid_date:
        if dob_date == valid_date:
            consistency_messages.append(
                "Date of birth and validity date "
                "are identical."
            )

    if consistency_messages:
        results.append({
            "field": "date_consistency",
            "valid": False,
            "status": "REVIEW",
            "severity": "HIGH",
            "message": " ".join(consistency_messages)
        })
    else:
        results.append({
            "field": "date_consistency",
            "valid": True,
            "status": "PASS",
            "severity": "LOW",
            "message": (
                "Licence dates are chronologically consistent."
            )
        })

    return results


def extract_vehicle_class(text):
    if not text:
        return ""

    text_upper = text.upper()

    classes = [
        "MCWG",
        "MCWOG",
        "LMV-NT",
        "LMV-TR",
        "LMV",
        "HGMV",
        "HTV",
        "HMV",
        "MGV",
        "TRANS",
        "PSV",
        "TRACTOR",
        "TRAILER"
    ]

    classes.sort(
        key=len,
        reverse=True
    )

    for vehicle_class in classes:
        pattern = (
            r"\b"
            + re.escape(vehicle_class)
            + r"\b"
        )

        if re.search(
            pattern,
            text_upper
        ):
            return vehicle_class

    return ""


def clean_vehicle_class(vehicle_class):
    if not vehicle_class:
        return ""

    value = vehicle_class.upper().strip()

    value = re.sub(
        r"[^A-Z0-9\-]",
        "",
        value
    )

    aliases = {
        "MCW/G": "MCWG",
        "MCW-G": "MCWG",
        "MCWG": "MCWG",
        "MCWOG": "MCWOG",
        "LMV": "LMV",
        "HMV": "HMV",
        "HGMV": "HGMV",
        "HTV": "HTV",
        "MGV": "MGV"
    }

    return aliases.get(
        value,
        value
    )