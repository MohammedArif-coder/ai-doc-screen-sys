def generate_evidence(validation_results, tampering_result=None):
    evidence = []

    # ==============================
    # VALIDATION EVIDENCE
    # ==============================

    for result in validation_results:

        field = result.get(
            "field",
            "unknown"
        )

        valid = result.get(
            "valid",
            True
        )

        status = result.get(
            "status"
        )

        message = result.get(
            "message",
            ""
        )

        # ==============================
        # QR / BARCODE EVIDENCE
        # ==============================

        if field == "qr_consistency":

            if status == "NOT_AVAILABLE":

                evidence.append({
                    "source": "qr_validation",
                    "field": field,
                    "status": "INFO",
                    "severity": "LOW",
                    "message": message
                })

            elif status == "PASS":

                evidence.append({
                    "source": "qr_validation",
                    "field": field,
                    "status": "PASS",
                    "severity": "LOW",
                    "message": message
                })

            # QR FAIL is handled by tampering analysis.
            # This prevents double-counting.

            continue

        # ==============================
        # VEHICLE CLASS
        # ==============================

        if field == "vehicle_class":

            if valid and status != "REVIEW":

                evidence.append({
                    "source": "validation",
                    "field": field,
                    "status": "PASS",
                    "severity": "LOW",
                    "message": message or (
                        "Vehicle class extracted successfully."
                    )
                })

            elif status == "REVIEW":

                evidence.append({
                    "source": "validation",
                    "field": field,
                    "status": "REVIEW",
                    "severity": "MEDIUM",
                    "message": message or (
                        "Vehicle class requires manual review."
                    )
                })

            else:

                evidence.append({
                    "source": "validation",
                    "field": field,
                    "status": "FAIL",
                    "severity": "HIGH",
                    "message": message or (
                        "Vehicle class validation failed."
                    )
                })

            continue

        # ==============================
        # NORMAL VALIDATION EVIDENCE
        # ==============================

        if valid and status != "FAIL":

            evidence.append({
                "source": "validation",
                "field": field,
                "status": "PASS",
                "severity": "LOW",
                "message": message or (
                    "Validation check passed."
                )
            })

        elif status == "REVIEW":

            evidence.append({
                "source": "validation",
                "field": field,
                "status": "REVIEW",
                "severity": "MEDIUM",
                "message": message or (
                    "This validation requires manual review."
                )
            })

        else:

            evidence.append({
                "source": "validation",
                "field": field,
                "status": "FAIL",
                "severity": "HIGH",
                "message": message or (
                    "Validation check failed."
                )
            })

    # ==============================
    # TAMPERING / FORENSIC EVIDENCE
    # ==============================

    if tampering_result:

        indicators = tampering_result.get(
            "indicators",
            []
        )

        for indicator in indicators:

            indicator_type = indicator.get(
                "type",
                "tampering"
            )

            status = indicator.get(
                "status",
                "REVIEW"
            )

            severity = indicator.get(
                "severity",
                "MEDIUM"
            )

            message = indicator.get(
                "message",
                ""
            )

            if not message:
                continue

            evidence.append({
                "source": "tampering",
                "field": indicator_type,
                "status": status,
                "severity": severity,
                "message": message
            })

    return evidence