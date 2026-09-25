def calculate_risk(evidence):
    high_count = 0
    medium_count = 0
    failed_count = 0
    review_count = 0

    reasons = []

    for item in evidence:
        status = item.get("status", "INFO")
        severity = item.get("severity", "LOW")
        message = item.get("message", "")

        if severity == "HIGH":
            high_count += 1

        elif severity == "MEDIUM":
            medium_count += 1

        if status == "FAIL":
            failed_count += 1

        if status == "REVIEW":
            review_count += 1

        if status in ["FAIL", "REVIEW"]:
            if message and message not in reasons:
                reasons.append(message)

    # -----------------------------------------------------
    # RISK DECISION
    # -----------------------------------------------------

    if high_count >= 2:
        status = "HIGH_REVIEW"

    elif high_count == 1:
        status = "REVIEW"

    elif review_count >= 1:
        status = "REVIEW"

    elif medium_count >= 2:
        status = "REVIEW"

    elif failed_count > 0:
        status = "REVIEW"

    else:
        status = "CLEAR"

    return {
        "status": status,
        "high_severity_count": high_count,
        "medium_severity_count": medium_count,
        "failed_evidence_count": failed_count,
        "review_evidence_count": review_count,
        "reasons": reasons
    }