import re

from app.modules.driving_license.ocr import (
    extract_ocr_with_confidence
)

from app.modules.driving_license.validation import (
    validate_licence_number,
    validate_dates,
    extract_vehicle_class,
    clean_vehicle_class
)

from app.modules.driving_license.qr_barcode import (
    detect_qr_barcode
)

from app.modules.driving_license.face import (
    detect_face
)

from app.modules.driving_license.forensics import (
    analyze_forensics
)

from app.modules.driving_license.tampering import (
    analyze_tampering
)

from app.intelligence.contradiction import (
    check_contradictions
)

from app.intelligence.evidence import (
    generate_evidence
)

from app.intelligence.risk import (
    calculate_risk
)

from app.intelligence.explanation import (
    generate_explanation
)


# ============================================================
# OCR HELPERS
# ============================================================

def normalize_ocr_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_date(date_text):
    if not date_text:
        return ""

    value = date_text.strip()
    value = value.replace("-", "/")
    value = value.replace(".", "/")

    match = re.search(
        r"\b(\d{2})/(\d{2})/(\d{4})\b",
        value
    )

    if not match:
        return ""

    return (
        f"{match.group(1)}/"
        f"{match.group(2)}/"
        f"{match.group(3)}"
    )


def clean_extracted_value(value):
    if not value:
        return ""

    value = value.strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip(" :;-|")


def extract_field(pattern, text):
    if not text:
        return ""

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if not match:
        return ""

    return clean_extracted_value(
        match.group(1)
    )


# ============================================================
# NAME
# ============================================================

def extract_name(text):

    patterns = [

        r"Name\s*:\s*(.*?)"
        r"(?=\s+S/D/W\s+of\b|\s+S/D/W\s*:|"
        r"\s+S/W/D\s*:|\s+W/O\b|\s+D/O\b|"
        r"\s+F/O\b|\s+C/O\b|\s+DOB\b|"
        r"\s+Blood\s+Group\b|\s+Address\b|$)",

        r"Name\s+(.*?)"
        r"(?=\s+S/D/W\s+of\b|\s+S/D/W\s*:|"
        r"\s+S/W/D\s*:|\s+W/O\b|\s+D/O\b|"
        r"\s+F/O\b|\s+C/O\b|\s+DOB\b|"
        r"\s+Blood\s+Group\b|\s+Address\b|$)"
    ]

    for pattern in patterns:

        value = extract_field(
            pattern,
            text
        )

        if value:
            return value

    return ""


# ============================================================
# GENERIC DATE EXTRACTION
# ============================================================

def extract_date_after_label(
    text,
    label_pattern
):

    pattern = (
        label_pattern
        + r"\s*[:\-]?\s*"
        + r"(\d{2}[\/\-\.]\d{2}[\/\-\.]\d{4})"
    )

    value = extract_field(
        pattern,
        text
    )

    return normalize_date(value)


# ============================================================
# DATE OF BIRTH
# ============================================================

def extract_dob(text):

    labels = [
        r"D\.?\s*O\.?\s*B\.?",
        r"Date\s+of\s+Birth"
    ]

    for label in labels:

        value = extract_date_after_label(
            text,
            label
        )

        if value:
            return value

    return ""


# ============================================================
# LICENCE NUMBER
# ============================================================

def extract_licence_number(text):

    patterns = [

        # Licence No / License No
        r"(?:Licence|License)\s*"
        r"(?:No\.?|Number)\s*"
        r"[:\-]?\s*"
        r"([A-Z0-9][A-Z0-9\-\/\s]{3,30}?)"
        r"(?=\s+(?:DOI|D\.?\s*O\.?\s*I\.?|"
        r"DOB|D\.?\s*O\.?\s*B\.?|"
        r"Date\s+of\s+Birth|Name|Validity|"
        r"Valid\s+Till|Vali\s+Till|Valid\s+Upto|"
        r"Issue\s+Date|Date\s+of\s+Issue|FORM)\b|$)",

        # DL No / DL Number
        r"\bDL\s*"
        r"(?:No\.?|Number)\s*"
        r"[:\-]?\s*"
        r"([A-Z0-9][A-Z0-9\-\/\s]{3,30}?)"
        r"(?=\s+(?:DOI|D\.?\s*O\.?\s*I\.?|"
        r"DOB|D\.?\s*O\.?\s*B\.?|"
        r"Date\s+of\s+Birth|Name|Validity|"
        r"Valid\s+Till|Vali\s+Till|Valid\s+Upto|"
        r"Issue\s+Date|Date\s+of\s+Issue|FORM)\b|$)",

        # OCR may read DL as DI / D1
        r"\bD[IL1]\s*"
        r"(?:No\.?|Number)\s*"
        r"[:\-]?\s*"
        r"([A-Z0-9][A-Z0-9\-\/\s]{3,30}?)"
        r"(?=\s+(?:DOI|D\.?\s*O\.?\s*I\.?|"
        r"DOB|D\.?\s*O\.?\s*B\.?|"
        r"Date\s+of\s+Birth|Name|Validity|"
        r"Valid\s+Till|Vali\s+Till|Valid\s+Upto|"
        r"Issue\s+Date|Date\s+of\s+Issue|FORM)\b|$)"
    ]

    for pattern in patterns:

        value = extract_field(
            pattern,
            text
        )

        if value:
            return value

    return ""


# ============================================================
# ISSUE DATE
# ============================================================

def extract_issue_date(text):

    labels = [
        r"Issue\s+Date",
        r"Date\s+of\s+Issue",
        r"D\.?\s*O\.?\s*I\.?"
    ]

    for label in labels:

        value = extract_date_after_label(
            text,
            label
        )

        if value:
            return value

    return ""


# ============================================================
# VALIDITY DATE
# ============================================================

def extract_valid_until(text):

    labels = [
        r"Validity\s+Till",
        r"Validity",
        r"Valid\s+Till",
        r"Vali\s+Till",
        r"Valid\s+Upto",
        r"Valid\s+Up\s+To",
        r"Expiry\s+Date",
        r"Expiry"
    ]

    for label in labels:

        value = extract_date_after_label(
            text,
            label
        )

        if value:
            return value

    return ""


# ============================================================
# QR / BARCODE CONSISTENCY
# ============================================================

def check_qr_consistency(
    qr_result,
    licence_number
):

    if not qr_result.get("detected"):

        return {
            "field": "qr_consistency",
            "status": "NOT_AVAILABLE",
            "valid": True,
            "message": (
                "No QR code or barcode was detected. "
                "Machine-readable consistency could not be checked."
            )
        }

    qr_data = qr_result.get("data")

    if not qr_data:

        return {
            "field": "qr_consistency",
            "status": "NOT_AVAILABLE",
            "valid": True,
            "message": (
                "A machine-readable code was detected, "
                "but no readable data was obtained."
            )
        }

    if not licence_number:

        return {
            "field": "qr_consistency",
            "status": "REVIEW",
            "valid": True,
            "message": (
                "Machine-readable data was detected, "
                "but the printed licence number could "
                "not be compared."
            )
        }

    qr_clean = re.sub(
        r"[^A-Z0-9]",
        "",
        qr_data.upper()
    )

    licence_clean = re.sub(
        r"[^A-Z0-9]",
        "",
        licence_number.upper()
    )

    if licence_clean in qr_clean:

        return {
            "field": "qr_consistency",
            "status": "PASS",
            "valid": True,
            "message": (
                "The QR/barcode data is consistent with "
                "the printed licence number."
            )
        }

    return {
        "field": "qr_consistency",
        "status": "FAIL",
        "valid": False,
        "message": (
            "The machine-readable QR/barcode data does not "
            "match the printed licence number."
        )
    }


# ============================================================
# MAIN PROCESSOR
# ============================================================

def process_driving_license(image_path: str):

    # --------------------------------------------------------
    # 1. OCR
    # --------------------------------------------------------

    ocr_result = extract_ocr_with_confidence(
        image_path
    )

    ocr_text = normalize_ocr_text(
        ocr_result["text"]
    )

    ocr_confidence = ocr_result[
        "average_confidence"
    ]


    # --------------------------------------------------------
    # 2. FIELD EXTRACTION
    # --------------------------------------------------------

    name = extract_name(
        ocr_text
    )

    dob = extract_dob(
        ocr_text
    )

    licence_number = extract_licence_number(
        ocr_text
    )

    issue_date = extract_issue_date(
        ocr_text
    )

    valid_until = extract_valid_until(
        ocr_text
    )


    # --------------------------------------------------------
    # 3. VEHICLE CLASS
    # --------------------------------------------------------

    vehicle_class = extract_vehicle_class(
        ocr_text
    )

    vehicle_class = clean_vehicle_class(
        vehicle_class
    )


    # --------------------------------------------------------
    # 4. FIELD OBJECT
    # --------------------------------------------------------

    fields = {

        "name": {
            "value": name,
            "confidence": ocr_confidence
        },

        "date_of_birth": {
            "value": dob,
            "confidence": ocr_confidence
        },

        "licence_number": {
            "value": licence_number,
            "confidence": ocr_confidence
        },

        "issue_date": {
            "value": issue_date,
            "confidence": ocr_confidence
        },

        "valid_until": {
            "value": valid_until,
            "confidence": ocr_confidence
        },

        "vehicle_class": {
            "value": vehicle_class,
            "confidence": ocr_confidence
        }
    }


    # --------------------------------------------------------
    # 5. VALIDATION
    # --------------------------------------------------------

    validation_results = []

    licence_validation = validate_licence_number(
        licence_number
    )

    validation_results.append(
        licence_validation
    )

    date_results = validate_dates(
        dob,
        issue_date,
        valid_until
    )

    validation_results.extend(
        date_results
    )


    # --------------------------------------------------------
    # 6. VEHICLE CLASS VALIDATION
    # --------------------------------------------------------

    if vehicle_class:

        validation_results.append({
            "field": "vehicle_class",
            "valid": True,
            "status": "PASS",
            "message": (
                f"Vehicle class extracted: "
                f"{vehicle_class}"
            )
        })

    else:

        validation_results.append({
            "field": "vehicle_class",
            "valid": False,
            "status": "REVIEW",
            "message": (
                "Vehicle class could not be extracted "
                "from the document."
            )
        })


    # --------------------------------------------------------
    # 7. QR / BARCODE
    # --------------------------------------------------------

    qr_result = detect_qr_barcode(
        image_path
    )

    qr_consistency = check_qr_consistency(
        qr_result,
        licence_number
    )

    validation_results.append(
        qr_consistency
    )


    # --------------------------------------------------------
    # 8. FACE / PHOTO
    # --------------------------------------------------------

    biometric_result = detect_face(
        image_path
    )


    # --------------------------------------------------------
    # 9. FORENSICS
    # --------------------------------------------------------

    forensic_result = analyze_forensics(
        image_path
    )


    # --------------------------------------------------------
    # 10. TAMPERING
    # --------------------------------------------------------

    tampering_result = analyze_tampering(
        qr_consistency,
        forensic_result
    )


    # --------------------------------------------------------
    # 11. CONTRADICTION CHECK
    # --------------------------------------------------------

    contradictions = check_contradictions(
        fields
    )


    # --------------------------------------------------------
    # 12. EVIDENCE
    # --------------------------------------------------------

    evidence = generate_evidence(
        validation_results,
        tampering_result
    )


    # --------------------------------------------------------
    # 13. BIOMETRIC EVIDENCE
    # --------------------------------------------------------

    if biometric_result.get("status") == "REVIEW":

        evidence.append({
            "source": "biometric",
            "field": "face_verification",
            "status": "REVIEW",
            "severity": "MEDIUM",
            "message": biometric_result.get(
                "message",
                "Face verification requires review."
            )
        })


    # --------------------------------------------------------
    # 14. RISK
    # --------------------------------------------------------

    risk_result = calculate_risk(
        evidence
    )


    # --------------------------------------------------------
    # 15. EXPLANATION
    # --------------------------------------------------------

    explanation = generate_explanation(
        risk_result,
        evidence,
        contradictions
    )


    # --------------------------------------------------------
    # 16. FINAL RESULT
    # --------------------------------------------------------

    return {

        "document_type":
            "DRIVING_LICENCE",

        "ocr_text":
            ocr_text,

        "ocr": {
            "average_confidence":
                ocr_confidence,

            "word_count":
                ocr_result.get(
                    "word_count",
                    0
                )
        },

        "fields":
            fields,

        "validation":
            validation_results,

        "qr_barcode":
            qr_result,

        "forensics":
            forensic_result,

        "biometric":
            biometric_result,

        "tampering":
            tampering_result,

        "contradictions":
            contradictions,

        "evidence":
            evidence,

        "risk":
            risk_result,

        "explanation":
            explanation,

        "module_status":
            "COMPLETE"
    }