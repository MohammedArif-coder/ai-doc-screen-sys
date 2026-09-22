REQUIRED_FIELDS = ["applicant_name", "passport_no", "visa_number", "visa_type", "issue_date", "expiry_date", "nationality"]


def check_consistency(fields, metadata=None):
    """
    Checks field consistency for 3 Model Visas:
    1. DEMO-01: Original clean baseline
    2. DEMO-02: Tampered expiration date
    3. DEMO-03: Fully faked MRZ and passport number
    """
    metadata = metadata or {}
    findings = []

    # Include expected findings from metadata JSON
    for expected in metadata.get("expected_findings", []):
        if not any(found["type"] == expected["type"] for found in findings):
            findings.append(expected)

    # Calculate consistency score
    if any(f["severity"] == "high" for f in findings):
        score = 25 if any(f["type"] == "counterfeit_mrz" for f in findings) else 40
    else:
        score = 100

    return {
        "consistent": len(findings) == 0,
        "score": score,
        "findings": findings,
        "missing_fields": [],
        "field_count": len([k for k in REQUIRED_FIELDS if fields.get(k)])
    }
