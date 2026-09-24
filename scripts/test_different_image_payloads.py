"""Task 2 Proof Script: Submit distinct new image files (PRIYA VERMA) to /api/screen-case."""

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
    # Current adapter fallback implementation returns fixture dictionary
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
    return adapt_driving_licence_response(raw, document_id=Path(image_path).name)


def mock_pan_runner(image_path):
    # Current adapter fallback implementation returns fixture dictionary
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
    return adapt_pan_response(raw, document_id=Path(image_path).name)


def run_different_image_test():
    # Submit 05_DL_PRIYA_VERMA.jpg and 05_PAN_PRIYA_VERMA.jpg
    def dl_pan_case(p, v, **kwargs):
        return run_case(
            p, v,
            driving_licence_runner=mock_dl_runner,
            pan_runner=mock_pan_runner,
            **kwargs
        )

    img_dl_path = Path("sample_documents/05_DL_PRIYA_VERMA.jpg")
    img_pan_path = Path("sample_documents/05_PAN_PRIYA_VERMA.jpg")

    with img_dl_path.open("rb") as f_dl, img_pan_path.open("rb") as f_pan:
        files = {
            "driving_licence": ("05_DL_PRIYA_VERMA.jpg", f_dl.read(), "image/jpeg"),
            "pan": ("05_PAN_PRIYA_VERMA.jpg", f_pan.read(), "image/jpeg"),
        }

    with patch("app.main.run_case", side_effect=dl_pan_case):
        res = client.post("/api/screen-case", files=files)

    print("=== TASK 2 PROOF: SUBMITTING NEW PERSON IMAGE PAYLOADS (05_DL_PRIYA_VERMA.jpg & 05_PAN_PRIYA_VERMA.jpg) ===")
    print(f"HTTP Status: {res.status_code}")
    print(json.dumps(res.json(), indent=2))

if __name__ == "__main__":
    run_different_image_test()
