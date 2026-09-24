"""Test script to hit /api/screen-case with DL and PAN payloads and dump raw API JSON responses."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "daksh-backend"))

from unittest.mock import patch
from fastapi.testclient import TestClient

from app.adapters.driving_licence_adapter import adapt_driving_licence_response
from app.adapters.pan_adapter import adapt_pan_response
from app.main import app
from app.services.case_service import run_case


client = TestClient(app)

def mock_dl_runner(image_path):
    raw = {
        "status": "completed",
        "visual_fields": {
            "dl_number": "MH1220150001234",
            "name": "RAHUL SHARMA",
            "dob": "1995-06-15",
            "issuing_authority": "RTO PUNE",
            "validity_date": "2035-06-14",
            "address": "45 M.G. ROAD PUNE MAHARASHTRA",
        },
        "quality": {"score": 95.0},
    }
    return adapt_driving_licence_response(raw, document_id="dl_sample.jpg")


def mock_pan_runner(image_path):
    raw = {
        "status": "completed",
        "visual_fields": {
            "pan_number": "ABCPK9876M",
            "name": "RAHUL SHARMA",
            "dob": "1995-06-15",
            "father_name": "RAMESH SHARMA",
        },
        "quality": {"score": 98.0},
    }
    return adapt_pan_response(raw, document_id="pan_sample.jpg")


def run_live_tests():
    # 1. Driving Licence Payload Test
    def dl_case(p, v, **kwargs):
        return run_case(
            p, v,
            driving_licence_runner=mock_dl_runner,
            **kwargs
        )

    files_dl = {
        "driving_licence": ("dl_sample.jpg", b"fake_dl_bytes", "image/jpeg"),
    }
    with patch("app.main.run_case", side_effect=dl_case):
        res_dl = client.post("/api/screen-case", files=files_dl)

    print("=== REAL API RESPONSE: DRIVING LICENCE PAYLOAD ===")
    print(json.dumps(res_dl.json(), indent=2))
    print("\n" + "="*50 + "\n")

    # 2. PAN Card Payload Test
    def pan_case(p, v, **kwargs):
        return run_case(
            p, v,
            pan_runner=mock_pan_runner,
            **kwargs
        )

    files_pan = {
        "pan": ("pan_sample.jpg", b"fake_pan_bytes", "image/jpeg"),
    }
    with patch("app.main.run_case", side_effect=pan_case):
        res_pan = client.post("/api/screen-case", files=files_pan)

    print("=== REAL API RESPONSE: PAN CARD PAYLOAD ===")
    print(json.dumps(res_pan.json(), indent=2))

if __name__ == "__main__":
    run_live_tests()
