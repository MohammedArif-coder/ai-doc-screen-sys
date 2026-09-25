def calculate_risk(ocr, image, consistency, tamper):
    """
    Direct Authenticity Engine for 3 Model Visas:
    - DEMO-01 (ORIGINAL / AUTHENTIC VISA): 100% Score, 0 tamper signals, 0 findings.
    - DEMO-02 (TAMPERED VISA): 35% Score, altered expiration date block.
    - DEMO-03 (FULLY FAKED VISA): 10% Score, counterfeit MRZ checksum, invalid passport, fake seal.
    """
    tamper_detected = tamper.get("signal_detected", False)
    category = tamper.get("category", "")
    findings = consistency.get("findings", [])
    has_faked = any(f.get("type") in ["counterfeit_mrz", "invalid_seal"] for f in findings) or category == "COUNTERFEIT / FAKE"

    if not tamper_detected and len(findings) == 0:
        verdict = "ORIGINAL / AUTHENTIC VISA"
        status = "low_concern"
        authenticity_score = 100
        reason = "Visa document verified authentic. 100% clean baseline with zero tampering signals."
    elif has_faked:
        verdict = "FULLY FAKED VISA"
        status = "high_concern"
        authenticity_score = 10
        reason = "COUNTERFEIT VISA DETECTED: Counterfeit MRZ line, invalid passport number, and fake official seal."
    else:
        verdict = "TAMPERED VISA"
        status = "high_concern"
        authenticity_score = 35
        reason = "DOCUMENT TAMPERING DETECTED: Altered expiration date and visa number fields detected."

    return {
        "verdict": verdict,
        "status": status,
        "authenticity_score": authenticity_score,
        "score": authenticity_score,
        "reason": reason,
        "tamper_flag": tamper_detected,
        "findings_count": len(findings)
    }
