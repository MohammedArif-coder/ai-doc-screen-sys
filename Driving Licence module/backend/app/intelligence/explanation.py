# --------------------------------------------------
# EXPLANATION GENERATION
# --------------------------------------------------

def generate_explanation(
    risk_result,
    evidence,
    contradictions
):

    status = risk_result.get(
        "status",
        "REVIEW"
    )

    reasons = []
    positive_checks = []

    # --------------------------------------------------
    # PROCESS EVIDENCE
    # --------------------------------------------------

    for item in evidence:

        item_status = item.get(
            "status",
            "INFO"
        )

        message = item.get(
            "message",
            ""
        )

        severity = item.get(
            "severity",
            "LOW"
        )

        # Review / failed evidence
        if item_status in [
            "FAIL",
            "REVIEW"
        ]:

            if message:

                reasons.append({
                    "source": item.get(
                        "source",
                        "unknown"
                    ),
                    "field": item.get(
                        "field",
                        ""
                    ),
                    "severity": severity,
                    "message": message
                })

        # Successful evidence
        elif item_status == "PASS":

            if message:

                positive_checks.append({
                    "source": item.get(
                        "source",
                        "unknown"
                    ),
                    "field": item.get(
                        "field",
                        ""
                    ),
                    "message": message
                })

    # --------------------------------------------------
    # PROCESS CONTRADICTIONS
    # --------------------------------------------------

    for contradiction in contradictions:

        message = contradiction.get(
            "message",
            ""
        )

        if not message:
            continue

        reasons.append({
            "source": "contradiction",
            "field": (
                contradiction.get(
                    "field_1",
                    ""
                )
                + "_"
                + contradiction.get(
                    "field_2",
                    ""
                )
            ),
            "severity": contradiction.get(
                "severity",
                "MEDIUM"
            ),
            "message": message
        })

    # --------------------------------------------------
    # REMOVE DUPLICATE REASONS
    # --------------------------------------------------

    unique_reasons = []

    seen_messages = set()

    for reason in reasons:

        message = reason.get(
            "message",
            ""
        )

        if message in seen_messages:
            continue

        seen_messages.add(
            message
        )

        unique_reasons.append(
            reason
        )

    reasons = unique_reasons

    # --------------------------------------------------
    # CLEAR
    # --------------------------------------------------

    if status == "CLEAR":

        summary = (
            "The driving licence passed the available "
            "automated validation checks. No significant "
            "anomaly requiring review was detected."
        )

        decision = "CLEAR"

        recommendation = (
            "No immediate review trigger was identified "
            "by the available automated checks."
        )

    # --------------------------------------------------
    # HIGH REVIEW
    # --------------------------------------------------

    elif status == "HIGH_REVIEW":

        summary = (
            "The driving licence contains multiple "
            "high-severity signals. Manual verification "
            "is recommended."
        )

        decision = "HIGH_REVIEW"

        recommendation = (
            "Review the highlighted evidence and verify "
            "the document against an authoritative source "
            "before making a final decision."
        )

    # --------------------------------------------------
    # NORMAL REVIEW
    # --------------------------------------------------

    else:

        summary = (
            "The driving licence contains one or more "
            "signals that require further review."
        )

        decision = "REVIEW"

        recommendation = (
            "Review the highlighted evidence and verify "
            "the document against an authoritative source "
            "before making a final decision."
        )

    # --------------------------------------------------
    # FINAL EXPLANATION
    # --------------------------------------------------

    return {
        "decision": decision,

        "summary": summary,

        "reasons": reasons,

        "positive_checks": positive_checks,

        "recommendation": recommendation
    }