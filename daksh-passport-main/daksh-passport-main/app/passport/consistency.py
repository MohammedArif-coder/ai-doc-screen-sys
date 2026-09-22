import re


def normalize_text(text):
    if text is None:
        return ""

    text = str(text).upper()
    text = text.replace("<", " ")
    text = re.sub(r"[^A-Z0-9 ]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_name(text):
    text = normalize_text(text)
    return text.replace(" ", "")


def date_to_mrz(date_text):
    """
    Convert DD/MM/YYYY -> YYMMDD
    """
    if not date_text:
        return None

    match = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", date_text.strip())

    if not match:
        return None

    day, month, year = match.groups()

    return year[2:4] + month + day


def compare_field(name, visual_value, mrz_value):
    visual = normalize_text(visual_value)
    mrz = normalize_text(mrz_value)

    if not visual or not mrz:
        return {
            "field": name,
            "status": "UNAVAILABLE",
            "visual": visual_value,
            "mrz": mrz_value
        }

    if visual == mrz:
        status = "MATCH"
    else:
        status = "MISMATCH"

    return {
        "field": name,
        "status": status,
        "visual": visual_value,
        "mrz": mrz_value
    }


def compare_passport_fields(visual, mrz):
    results = []

    # Passport number
    results.append(
        compare_field(
            "passport_number",
            visual.get("passport_number"),
            mrz.get("passport_number")
        )
    )

    # Country code
    results.append(
        compare_field(
            "country_code",
            visual.get("country_code"),
            mrz.get("issuing_country")
        )
    )

    # Sex
    results.append(
        compare_field(
            "sex",
            visual.get("sex"),
            mrz.get("sex")
        )
    )

    # Date of birth
    visual_dob = date_to_mrz(visual.get("date_of_birth"))

    results.append(
        compare_field(
            "date_of_birth",
            visual_dob,
            mrz.get("date_of_birth")
        )
    )

    # Expiry date
    visual_expiry = date_to_mrz(visual.get("expiry_date"))

    results.append(
        compare_field(
            "expiry_date",
            visual_expiry,
            mrz.get("expiry_date")
        )
    )

    # Name
    visual_name = normalize_name(visual.get("name"))
    mrz_name = normalize_name(
        str(mrz.get("surname", "")) + str(mrz.get("given_names", ""))
    )

    if visual_name and mrz_name:
        if visual_name == mrz_name:
            name_status = "MATCH"
        elif visual_name in mrz_name or mrz_name in visual_name:
            name_status = "PARTIAL"
        else:
            name_status = "MISMATCH"

        results.append({
            "field": "name",
            "status": name_status,
            "visual": visual.get("name"),
            "mrz": (
                str(mrz.get("surname", "")) +
                " " +
                str(mrz.get("given_names", ""))
            )
        })
    else:
        results.append({
            "field": "name",
            "status": "UNAVAILABLE",
            "visual": visual.get("name"),
            "mrz": ""
        })

    return results