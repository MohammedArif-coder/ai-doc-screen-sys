def check_contradictions(fields):
    """
    Check for contradictions between extracted fields.
    """

    contradictions = []

    dob = fields.get("date_of_birth", {}).get("value")
    valid_until = fields.get("valid_until", {}).get("value")

    if dob and valid_until:
        if dob == valid_until:
            contradictions.append({
                "field_1": "date_of_birth",
                "field_2": "valid_until",
                "severity": "HIGH",
                "message": "Date of birth and validity date are identical."
            })

    return contradictions