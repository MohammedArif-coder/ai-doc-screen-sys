def analyze_tampering(
    qr_consistency,
    forensic_result
):

    indicators = []

    # ========================================================
    # QR / BARCODE CONSISTENCY
    # ========================================================

    qr_status = qr_consistency.get(
        "status",
        "NOT_AVAILABLE"
    )

    if qr_status == "FAIL":

        indicators.append({
            "type": "QR_PRINTED_MISMATCH",
            "severity": "HIGH",
            "status": "REVIEW",
            "message": (
                "The machine-readable QR/barcode data "
                "does not match the printed licence number."
            )
        })

    elif qr_status == "PASS":

        indicators.append({
            "type": "QR_PRINTED_MATCH",
            "severity": "LOW",
            "status": "PASS",
            "message": (
                "The QR/barcode data is consistent "
                "with the printed licence number."
            )
        })

    # ========================================================
    # ACTUAL FORENSIC TAMPERING SIGNALS ONLY
    # ========================================================

    forensic_signals = forensic_result.get(
        "tampering_signals",
        []
    )

    for signal in forensic_signals:

        signal_type = signal.get(
            "type",
            "UNKNOWN"
        )

        severity = signal.get(
            "severity",
            "MEDIUM"
        )

        message = signal.get(
            "message",
            "A forensic tampering signal was detected."
        )

        indicators.append({
            "type": signal_type,
            "severity": severity,
            "status": "REVIEW",
            "message": message
        })

    # ========================================================
    # SUSPICIOUS REGIONS
    # ========================================================

    suspicious_regions = forensic_result.get(
        "suspicious_regions",
        []
    )

    if suspicious_regions:

        indicators.append({
            "type": "SUSPICIOUS_EDITED_REGION",
            "severity": "MEDIUM",
            "status": "REVIEW",
            "region_count": len(
                suspicious_regions
            ),
            "regions": suspicious_regions,
            "message": (
                f"{len(suspicious_regions)} suspicious "
                "document region(s) require manual review "
                "for possible editing or alteration."
            )
        })

    # ========================================================
    # PHOTO ANOMALIES
    # ========================================================

    photo_anomalies = forensic_result.get(
        "photo_anomalies",
        []
    )

    if photo_anomalies:

        indicators.append({
            "type": "PHOTO_REGION_ANOMALY",
            "severity": "MEDIUM",
            "status": "REVIEW",
            "region_count": len(
                photo_anomalies
            ),
            "regions": photo_anomalies,
            "message": (
                "The photograph region shows a "
                "visual inconsistency requiring "
                "manual review."
            )
        })

    # ========================================================
    # COUNT SEVERITIES
    # ========================================================

    high_count = sum(
        1
        for item in indicators
        if item.get("severity") == "HIGH"
    )

    medium_count = sum(
        1
        for item in indicators
        if item.get("severity") == "MEDIUM"
    )

    # ========================================================
    # FINAL TAMPERING STATUS
    # ========================================================

    if high_count >= 1:
        status = "REVIEW"

    elif medium_count >= 1:
        status = "REVIEW"

    else:
        status = "NORMAL"

    return {
        "status": status,
        "high_indicator_count": high_count,
        "medium_indicator_count": medium_count,
        "indicator_count": len(indicators),
        "indicators": indicators
    }