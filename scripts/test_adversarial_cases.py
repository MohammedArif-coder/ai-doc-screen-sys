"""Adversarial cross-document contradiction tests for DL and PAN modules."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "daksh-backend"))

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.adapters.aadhaar_adapter import adapt_aadhaar_response
from app.adapters.driving_licence_adapter import adapt_driving_licence_response
from app.adapters.pan_adapter import adapt_pan_response
from app.adapters.passport_adapter import adapt_passport_response
from app.main import app
from app.services.case_service import run_case


client = TestClient(app)

def run_adversarial_tests():
    # Adversarial Case 1: Aadhaar + PAN with Name & DOB mismatch
    # Aadhaar: Name="RAHUL SHARMA", DOB="1995-06-15"
    # PAN: Name="RAHUL SHARMAA", DOB="1995-06-20"
    def mock_aadhaar_1(_):
        raw = {
            "module_status": "completed",
            "fields": {
                "name": {"value": "RAHUL SHARMA", "confidence": 0.98},
                "dob": {"value": "1995-06-15", "confidence": 0.99},
            }
        }
        return adapt_aadhaar_response(raw, document_id="aadhaar_adv.jpg")

    def mock_pan_1(_):
        raw = {
            "status": "completed",
            "visual_fields": {
                "pan_number": "ABCPK9876M",
                "name": "RAHUL SHARMAA",
                "dob": "1995-06-20",
                "father_name": "RAMESH SHARMA",
            }
        }
        return adapt_pan_response(raw, document_id="pan_adv.jpg")

    def run_case_adv1(p, v, **kwargs):
        return run_case(
            p, v,
            aadhaar_runner=mock_aadhaar_1,
            pan_runner=mock_pan_1,
            **kwargs
        )

    files_1 = {
        "aadhaar": ("aadhaar_adv.jpg", b"fake_bytes", "image/jpeg"),
        "pan": ("pan_adv.jpg", b"fake_bytes", "image/jpeg"),
    }
    with patch("app.main.run_case", side_effect=run_case_adv1):
        res1 = client.post("/api/screen-case", files=files_1)

    print("=== ADVERSARIAL TEST 1: AADHAAR + PAN NAME & DOB MISMATCH ===")
    print(f"HTTP Status: {res1.status_code}")
    print(json.dumps(res1.json(), indent=2))
    print("\n" + "="*60 + "\n")

    # Adversarial Case 2: Passport + Driving Licence with DOB mismatch
    # Passport: DOB="1990-01-01", Name="JOHN DOE", Passport="Z8942103"
    # Driving Licence: DOB="1995-06-15", Name="JOHN DOE", DL="MH1220150001234"
    def mock_passport_2(_):
        raw = {
            "status": "completed",
            "visual_fields": {
                "passport_number": "Z8942103",
                "name": "JOHN DOE",
                "dob": "1990-01-01",
            }
        }
        return adapt_passport_response(raw, document_id="passport_adv.jpg")

    def mock_dl_2(_):
        raw = {
            "status": "completed",
            "visual_fields": {
                "dl_number": "MH1220150001234",
                "name": "JOHN DOE",
                "dob": "1995-06-15",
                "issuing_authority": "RTO PUNE",
            }
        }
        return adapt_driving_licence_response(raw, document_id="dl_adv.jpg")

    def run_case_adv2(p, v, **kwargs):
        return run_case(
            p, v,
            passport_runner=mock_passport_2,
            driving_licence_runner=mock_dl_2,
            **kwargs
        )

    files_2 = {
        "passport": ("passport_adv.jpg", b"fake_bytes", "image/jpeg"),
        "driving_licence": ("dl_adv.jpg", b"fake_bytes", "image/jpeg"),
    }
    with patch("app.main.run_case", side_effect=run_case_adv2):
        res2 = client.post("/api/screen-case", files=files_2)

    print("=== ADVERSARIAL TEST 2: PASSPORT + DRIVING LICENCE DOB MISMATCH ===")
    print(f"HTTP Status: {res2.status_code}")
    print(json.dumps(res2.json(), indent=2))

if __name__ == "__main__":
    run_adversarial_tests()
