import json
import os

from pan_ocr import extract_text
from pan_extractor import extract_pan_fields
from pan_validator import validate_pan_fields
from pan_forensics import analyze_pan_image
from pan_biometric import analyze_photo_region


def create_evidence(validation, forensics, biometric):
    evidence = []

    # PAN format
    if validation["pan_format"]:
        evidence.append({
            "source": "validation",
            "check": "PAN format",
            "result": "PASS",
            "message": "PAN number follows the expected format."
        })
    else:
        evidence.append({
            "source": "validation",
            "check": "PAN format",
            "result": "FLAG",
            "message": "PAN number does not follow the expected format."
        })

    # Name
    if validation["name_present"]:
        evidence.append({
            "source": "validation",
            "check": "Name",
            "result": "PASS",
            "message": "Name was successfully extracted."
        })
    else:
        evidence.append({
            "source": "validation",
            "check": "Name",
            "result": "FLAG",
            "message": "Name could not be extracted."
        })

    # Father's name
    if validation["father_name_present"]:
        evidence.append({
            "source": "validation",
            "check": "Father's name",
            "result": "PASS",
            "message": "Father's name was successfully extracted."
        })
    else:
        evidence.append({
            "source": "validation",
            "check": "Father's name",
            "result": "FLAG",
            "message": "Father's name could not be extracted."
        })

    # DOB
    if validation["dob_format"]:
        evidence.append({
            "source": "validation",
            "check": "Date of birth",
            "result": "PASS",
            "message": "Date of birth follows the expected format."
        })
    else:
        evidence.append({
            "source": "validation",
            "check": "Date of birth",
            "result": "FLAG",
            "message": "Date of birth format is invalid."
        })

    # Forensics
    if forensics["status"] == "NO_BASIC_FORENSIC_FLAGS":
        evidence.append({
            "source": "forensics",
            "check": "Basic image analysis",
            "result": "PASS",
            "message": "No basic forensic flags were detected."
        })

    elif forensics["status"] == "REVIEW":
        evidence.append({
            "source": "forensics",
            "check": "Image manipulation analysis",
            "result": "REVIEW",
            "message": "Forensic analysis produced a review signal."
        })

    else:
        evidence.append({
            "source": "forensics",
            "check": "Image analysis",
            "result": "INCONCLUSIVE",
            "message": "Image quality or available evidence was insufficient for a clear forensic result."
        })

    # Reference comparison
    reference = forensics.get("reference_comparison")

    if reference is not None:

        if reference["reference_status"] == "REVIEW":
            evidence.append({
                "source": "forensics",
                "check": "Reference image comparison",
                "result": "REVIEW",
                "message": "Significant image differences were detected compared with the available reference."
            })

        elif reference["reference_status"] == "NO_SIGNIFICANT_CHANGE":
            evidence.append({
                "source": "forensics",
                "check": "Reference image comparison",
                "result": "PASS",
                "message": "No significant difference was detected from the available reference."
            })

        elif reference["reference_status"] == "REFERENCE_NOT_AVAILABLE":
            evidence.append({
                "source": "forensics",
                "check": "Reference image comparison",
                "result": "NOT_CHECKED",
                "message": "Reference image was not available for comparison."
            })

    # Suspicious regions
    suspicious = forensics.get("suspicious_regions")

    if suspicious:
        suspicious_list = suspicious.get("suspicious_regions", [])

        if suspicious_list:
            evidence.append({
                "source": "forensics",
                "check": "Suspicious regions",
                "result": "REVIEW",
                "message": "Changes were detected in: " + ", ".join(suspicious_list)
            })

        else:
            evidence.append({
                "source": "forensics",
                "check": "Suspicious regions",
                "result": "PASS",
                "message": "No significant regional changes were detected."
            })

    # Biometric/photo region
    if biometric["photo_region_detected"]:
        evidence.append({
            "source": "biometric",
            "check": "Photo region",
            "result": "PASS",
            "message": "A usable photo region was detected."
        })
    else:
        evidence.append({
            "source": "biometric",
            "check": "Photo region",
            "result": "REVIEW",
            "message": "A usable photo region could not be confirmed."
        })

    return evidence


def determine_module_status(validation, forensics, biometric):

    if validation["issues"]:
        return "REVIEW"

    if forensics["status"] == "REVIEW":
        return "REVIEW"

    if forensics["status"] == "INCONCLUSIVE":
        return "INCONCLUSIVE"

    if biometric["status"] != "PHOTO_REGION_AVAILABLE":
        return "REVIEW"

    return "COMPLETE"


def run_pan_pipeline(image_path, case_id="CASE001", reference_path=None):

    # Step 1: OCR
    ocr_text = extract_text(image_path)

    # Step 2: Extract fields
    fields = extract_pan_fields(ocr_text)

    # Step 3: Validate fields
    validation = validate_pan_fields(fields)

    # Step 4: Forensic analysis
    forensics = analyze_pan_image(
        image_path,
        reference_path
    )

    # Step 5: Photo-region analysis
    biometric = analyze_photo_region(image_path)

    # Step 6: Evidence generation
    evidence = create_evidence(
        validation,
        forensics,
        biometric
    )

    # Step 7: Final module status
    module_status = determine_module_status(
        validation,
        forensics,
        biometric
    )

    # Standard P4 output
    result = {
        "case_id": case_id,
        "document_type": "PAN",
        "fields": fields,
        "validation": validation,
        "forensics": forensics,
        "biometric": biometric,
        "evidence": evidence,
        "module_status": module_status
    }

    return result


if __name__ == "__main__":

    # TEST 1: CLEAN PAN
    image_path = "input/dummy_pan.png"

    # Use the same clean PAN as the trusted reference.
    # Therefore, no artificial difference should be detected.
    reference_path = "input/dummy_pan.png"

    result = run_pan_pipeline(
        image_path=image_path,
        case_id="TEST_CLEAN_PAN",
        reference_path=reference_path
    )

    print("\n========== DAKSH PAN CLEAN TEST ==========")

    print(json.dumps(result, indent=4))

    # Save result
    os.makedirs("output", exist_ok=True)

    output_file = "output/clean_pan_test_result.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4)

    print("\n==========================================")
    print("Clean PAN test completed.")
    print("Result saved to:", output_file)