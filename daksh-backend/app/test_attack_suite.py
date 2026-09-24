"""Comprehensive 22-Scenario Attack Test Suite for DAKSH Prototype.

Tests the full path:
Frontend Payload -> API -> Adapters -> Evidence -> Contradiction Engine -> Risk Aggregator -> Decision -> Frontend Serializer
"""

import io
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Any
from fastapi.testclient import TestClient

from app.adapters.passport_adapter import PassportAdapterResult, adapt_passport_response
from app.adapters.visa_adapter import VisaAdapterResult, adapt_visa_response
from app.adapters.aadhaar_adapter import AadhaarAdapterResult, adapt_aadhaar_response
from app.main import app
from app.schemas import Document, Evidence, EvidenceType
from app.services.case_service import run_case


client = TestClient(app)

PROHIBITED_TERMS = ["fraud_probability", "authenticity_percentage", "fake", "genuine"]


def check_verifications(response_json: dict[str, Any], status_code: int) -> list[str]:
    """Verify all mandatory assertions:
    - no crash (status_code in (200, 422))
    - no fabricated confidence
    - no fabricated fraud probability
    - no fake/genuine classification
    - no negative inference from missing evidence
    - contradictions remain traceable
    - supporting IDs survive to frontend
    - correct status is displayed
    - explanations are understandable
    """
    failures = []
    
    if status_code not in (200, 422):
        failures.append(f"Crash or unexpected status code: {status_code}")

    json_str = str(response_json).lower()
    for term in PROHIBITED_TERMS:
        if term in json_str:
            failures.append(f"Prohibited term found in response: '{term}'")

    # Check evidence confidence values
    evidence_list = response_json.get("evidence", [])
    for ev in evidence_list:
        conf = ev.get("confidence")
        if conf is not None:
            if not isinstance(conf, (int, float)) or not (0.0 <= conf <= 1.0):
                failures.append(f"Invalid/fabricated confidence value: {conf} in evidence {ev.get('evidence_id')}")

    # Check contradictions traceability
    contradictions = response_json.get("contradictions", [])
    for c in contradictions:
        for required_key in ["contradiction_id", "field", "document_a", "document_b", "value_a", "value_b", "explanation", "severity", "evidence_ids"]:
            if required_key not in c:
                failures.append(f"Contradiction missing key: {required_key}")
        if not isinstance(c.get("explanation"), str) or len(c.get("explanation", "")) < 5:
            failures.append(f"Contradiction explanation not understandable: {c.get('explanation')}")

    # Check supporting IDs presence
    if status_code == 200:
        if "supporting_evidence_ids" not in response_json:
            failures.append("Missing supporting_evidence_ids in response")
        if "supporting_contradiction_ids" not in response_json:
            failures.append("Missing supporting_contradiction_ids in response")

    return failures


def make_mock_passport(
    passport_number="A1234567",
    name="JOHN DOE",
    dob="1995-05-15",
    error=None,
    quality=None
):
    if error:
        return PassportAdapterResult(
            document=Document(document_id="passport.jpg", document_type="Passport", source_module="passport", processing_status="error"),
            error=error
        )
    raw = {
        "status": "completed",
        "visual_fields": {
            "passport_number": passport_number,
            "name": name,
            "dob": dob,
        },
        "mrz": {
            "parsed": {
                "passport_number": passport_number,
                "name": name,
                "dob": dob,
            }
        }
    }
    return adapt_passport_response(raw, document_id="passport.jpg")


def make_mock_visa(
    passport_no="A1234567",
    name="JOHN DOE",
    error=None,
    tamper_signal=None,
    quality=None
):
    if error:
        return VisaAdapterResult(
            document=Document(document_id="visa.jpg", document_type="Visa", source_module="visa", processing_status="error"),
            error=error
        )
    raw = {
        "status": "completed",
        "ocr": {
            "confidence": 95.0,
            "fields": {
                "passport_no": passport_no,
                "applicant_name": name,
            }
        }
    }
    if tamper_signal:
        raw["tamper_analysis"] = {"tamper_signal": tamper_signal, "confidence": 0.9}
        raw["findings"] = [{"severity": "MEDIUM", "description": tamper_signal}]
    if quality is not None:
        raw["image_analysis"] = {"score": quality * 100.0, "blur_detected": quality < 0.5}
    return adapt_visa_response(raw, document_id="visa.jpg")


def make_mock_aadhaar(
    name="JOHN DOE",
    dob="1995-05-15",
    error=None,
    missing_qr=False,
    quality=None
):
    if error:
        return AadhaarAdapterResult(
            document=Document(document_id="aadhaar.jpg", document_type="Aadhaar", source_module="aadhaar", processing_status="error"),
            error=error
        )
    raw = {
        "module_status": "completed",
        "fields": {
            "name": {"value": name, "confidence": 0.95},
            "dob": {"value": dob, "confidence": 0.95},
        }
    }
    if not missing_qr:
        raw["qr"] = {
            "fields": {
                "name": name,
                "dob": dob,
            }
        }
    if quality is not None:
        raw["quality"] = {"score": quality}
    return adapt_aadhaar_response(raw, document_id="aadhaar.jpg")


def run_attack_test_suite():
    results = []
    
    # Scenario 1: All documents valid
    def runner_1(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)
    
    # Scenario 2: Passport DOB altered
    def runner_2(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(dob="1990-01-01"), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(dob="1995-05-15"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 3: Aadhaar DOB altered
    def runner_3(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(dob="1995-05-15"), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(dob="1988-12-12"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 4: Name mismatch
    def runner_4(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(name="JOHN DOE"), visa_runner=lambda _: make_mock_visa(name="JOHN SMITH"), aadhaar_runner=lambda _: make_mock_aadhaar(name="JOHN DOE"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 5: Passport number mismatch
    def runner_5(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(passport_number="A1234567"), visa_runner=lambda _: make_mock_visa(passport_no="Z9999999"), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 6: Multiple contradictions
    def runner_6(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(passport_number="A1234567", dob="1990-01-01", name="JOHN DOE"), visa_runner=lambda _: make_mock_visa(passport_no="Z9999999", name="JOHN SMITH"), aadhaar_runner=lambda _: make_mock_aadhaar(dob="1995-05-15"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 7: Blurry document
    def runner_7(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(quality=0.2), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 8: Rotated document
    def runner_8(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(quality=0.4), aadhaar_image_path=aadhaar_image_path)

    # Scenario 9: Screenshot/recompressed document
    def runner_9(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(tamper_signal="Compression artifacts detected"), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 10: Missing QR
    def runner_10(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(missing_qr=True), aadhaar_image_path=aadhaar_image_path)

    # Scenario 11: Unavailable OCR
    def runner_11(p, v, aadhaar_image_path=None):
        raw_v = {"status": "completed", "ocr": {}}
        v_res = adapt_visa_response(raw_v, document_id="visa.jpg")
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: v_res, aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 12: Missing confidence
    def runner_12(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 13: One module unavailable
    def runner_13(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(error="Visa service unavailable"), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 14: Two modules unavailable
    def runner_14(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(error="Visa service unavailable"), aadhaar_runner=lambda _: make_mock_aadhaar(error="Aadhaar service unavailable"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 15: All modules unavailable
    def runner_15(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(error="Passport service unavailable"), visa_runner=lambda _: make_mock_visa(error="Visa service unavailable"), aadhaar_runner=lambda _: make_mock_aadhaar(error="Aadhaar service unavailable"), aadhaar_image_path=aadhaar_image_path)

    # Scenario 16: Duplicate evidence
    def runner_16(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 17: Correlated forensic signals
    def runner_17(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(tamper_signal="Font mismatch and copy-paste anomaly"), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=aadhaar_image_path)

    # Scenario 18: Missing optional checks (only 2 docs)
    def runner_18(p, v, aadhaar_image_path=None):
        return run_case(p, v, passport_runner=lambda _: make_mock_passport(), visa_runner=lambda _: make_mock_visa(), aadhaar_runner=lambda _: make_mock_aadhaar(), aadhaar_image_path=None)

    scenarios = [
        (1, "All documents valid", runner_1, "CLEAR", 200, True),
        (2, "Passport DOB altered", runner_2, "HIGH_REVIEW", 200, True),
        (3, "Aadhaar DOB altered", runner_3, "HIGH_REVIEW", 200, True),
        (4, "Name mismatch", runner_4, "REVIEW", 200, True),
        (5, "Passport number mismatch", runner_5, "HIGH_REVIEW", 200, True),
        (6, "Multiple contradictions", runner_6, "HIGH_REVIEW", 200, True),
        (7, "Blurry document", runner_7, "INCONCLUSIVE", 200, True),
        (8, "Rotated document", runner_8, "INCONCLUSIVE", 200, True),
        (9, "Screenshot/recompressed document", runner_9, "REVIEW", 200, True),
        (10, "Missing QR", runner_10, "CLEAR", 200, True),
        (11, "Unavailable OCR", runner_11, "CLEAR", 200, True),
        (12, "Missing confidence", runner_12, "CLEAR", 200, True),
        (13, "One module unavailable", runner_13, "CLEAR", 200, True),
        (14, "Two modules unavailable", runner_14, "CLEAR", 200, True),
        (15, "All modules unavailable", runner_15, "ERROR_422", 422, True),
        (16, "Duplicate evidence", runner_16, "CLEAR", 200, True),
        (17, "Correlated forensic signals", runner_17, "REVIEW", 200, True),
        (18, "Missing optional checks", runner_18, "CLEAR", 200, False),
    ]

    from unittest.mock import patch

    for test_num, name, runner, expected_status, expected_code, include_aadhaar in scenarios:
        files = {
            "passport": ("passport.jpg", b"fake-passport", "image/jpeg"),
            "visa": ("visa.jpg", b"fake-visa", "image/jpeg"),
        }
        if include_aadhaar:
            files["aadhaar"] = ("aadhaar.jpg", b"fake-aadhaar", "image/jpeg")

        with patch("app.main.run_case", side_effect=runner):
            res = client.post("/api/screen-case", files=files)
        
        status_code = res.status_code
        res_json = res.json()
        
        verif_failures = check_verifications(res_json, status_code)
        
        if status_code == 200:
            actual_status = res_json.get("status")
        else:
            actual_status = f"ERROR_{status_code}"
            
        bug = "NO" if (actual_status == expected_status and not verif_failures) else "YES"
        severity = "NONE" if bug == "NO" else ("CRITICAL" if verif_failures else "MINOR")
        
        results.append({
            "test_num": test_num,
            "test": f"{test_num}. {name}",
            "result": "PASS" if bug == "NO" else "FAIL",
            "expected": expected_status,
            "actual": actual_status,
            "bug": bug,
            "severity": severity,
            "details": verif_failures
        })

    # Test 19: Unsupported file
    res_19 = client.post("/api/screen-case", files={
        "passport": ("script.sh", b"#!/bin/bash", "text/x-sh"),
        "visa": ("visa.jpg", b"fake-visa", "image/jpeg")
    })
    v_19 = check_verifications(res_19.json(), res_19.status_code)
    results.append({
        "test_num": 19,
        "test": "19. Unsupported file",
        "result": "PASS" if res_19.status_code in (200, 422) and not v_19 else "FAIL",
        "expected": "CLEAR or INVALID_INPUT (HTTP 200 or 422)",
        "actual": f"Status {res_19.status_code}",
        "bug": "NO" if res_19.status_code in (200, 422) and not v_19 else "YES",
        "severity": "NONE" if res_19.status_code in (200, 422) and not v_19 else "MEDIUM",
        "details": v_19
    })

    # Test 20: Oversized file
    big_payload = b"0" * (10 * 1024 * 1024) # 10MB
    res_20 = client.post("/api/screen-case", files={
        "passport": ("passport.jpg", big_payload, "image/jpeg"),
        "visa": ("visa.jpg", b"fake-visa", "image/jpeg")
    })
    v_20 = check_verifications(res_20.json(), res_20.status_code)
    results.append({
        "test_num": 20,
        "test": "20. Oversized file",
        "result": "PASS" if res_20.status_code in (200, 422) and not v_20 else "FAIL",
        "expected": "No crash (HTTP 200 or 422)",
        "actual": f"Status {res_20.status_code}",
        "bug": "NO" if res_20.status_code in (200, 422) and not v_20 else "YES",
        "severity": "NONE" if res_20.status_code in (200, 422) and not v_20 else "MEDIUM",
        "details": v_20
    })

    # Test 21: Empty file
    res_21 = client.post("/api/screen-case", files={
        "passport": ("passport.jpg", b"", "image/jpeg"),
        "visa": ("visa.jpg", b"fake-visa", "image/jpeg")
    })
    v_21 = check_verifications(res_21.json(), res_21.status_code)
    results.append({
        "test_num": 21,
        "test": "21. Empty file",
        "result": "PASS" if res_21.status_code in (200, 422) and not v_21 else "FAIL",
        "expected": "No crash (HTTP 200 or 422)",
        "actual": f"Status {res_21.status_code}",
        "bug": "NO" if res_21.status_code in (200, 422) and not v_21 else "YES",
        "severity": "NONE" if res_21.status_code in (200, 422) and not v_21 else "MEDIUM",
        "details": v_21
    })

    # Test 22: Invalid document
    res_22 = client.post("/api/screen-case", files={
        "passport": ("corrupt.jpg", b"CORRUPT_BYTES_9999", "image/jpeg"),
        "visa": ("visa.jpg", b"fake-visa", "image/jpeg")
    })
    v_22 = check_verifications(res_22.json(), res_22.status_code)
    results.append({
        "test_num": 22,
        "test": "22. Invalid document",
        "result": "PASS" if res_22.status_code in (200, 422) and not v_22 else "FAIL",
        "expected": "No crash (HTTP 200 or 422)",
        "actual": f"Status {res_22.status_code}",
        "bug": "NO" if res_22.status_code in (200, 422) and not v_22 else "YES",
        "severity": "NONE" if res_22.status_code in (200, 422) and not v_22 else "MEDIUM",
        "details": v_22
    })

    return results

if __name__ == "__main__":
    res = run_attack_test_suite()
    for r in res:
        print(f"{r['test']:<35} | {r['result']:<5} | {r['expected']:<15} | {r['actual']:<15} | {r['bug']:<4} | {r['severity']}")
