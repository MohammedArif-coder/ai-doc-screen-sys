import os
import sys
import json
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT_DIR / "sample_documents"

MODULES = [
    {
        "id": "aadhaar",
        "name": "Aadhaar",
        "port": 8001,
        "sample": SAMPLE_DIR / "01_AADHAAR_MATCH.jpg",
        "adapter_fn": "screen_aadhaar_file",
    },
    {
        "id": "passport",
        "name": "Passport",
        "port": 8002,
        "sample": SAMPLE_DIR / "01_PASSPORT_MATCH.jpg",
        "adapter_fn": "screen_passport_file",
    },
    {
        "id": "visa",
        "name": "Visa",
        "port": 5000,
        "sample": SAMPLE_DIR / "01_VISA_MATCH.jpg",
        "adapter_fn": "screen_visa_file",
    },
    {
        "id": "dl",
        "name": "Driving Licence",
        "port": 8004,
        "sample": SAMPLE_DIR / "05_DL_PRIYA_VERMA.jpg",
        "adapter_fn": "screen_driving_licence_file",
    },
    {
        "id": "pan",
        "name": "PAN",
        "port": 8005,
        "sample": SAMPLE_DIR / "05_PAN_PRIYA_VERMA.jpg",
        "adapter_fn": "screen_pan_file",
    },
]


def check_health():
    print("=== 1. HEALTH CHECK STATUS ===")
    status_summary = {}
    for m in MODULES + [{"id": "daksh", "name": "DAKSH Central Backend", "port": 8000}]:
        url = f"http://127.0.0.1:{m['port']}/api/health"
        try:
            r = requests.get(url, timeout=2.0)
            if r.status_code == 200:
                print(f"[ONLINE] {m['name']} (Port {m['port']}) -> HTTP 200")
                status_summary[m['id']] = "ONLINE"
            else:
                print(f"[DEGRADED] {m['name']} (Port {m['port']}) -> HTTP {r.status_code}")
                status_summary[m['id']] = f"HTTP {r.status_code}"
        except Exception as e:
            print(f"[OFFLINE] {m['name']} (Port {m['port']}) -> Unreachable ({e})")
            status_summary[m['id']] = "OFFLINE"
    return status_summary


def test_adapters_and_backend():
    print("\n=== 2. REAL END-TO-END TEST RESULTS ===")
    sys.path.insert(0, str(ROOT_DIR / "daksh-backend"))

    results = []
    for m in MODULES:
        sample_path = m["sample"]
        name = m["name"]
        port = m["port"]

        if not sample_path.exists():
            print(f"Sample file missing for {name}: {sample_path}")
            continue

        print(f"\nTesting {name} with real sample: {sample_path.name}...")
        
        # Test adapter function directly
        if m["id"] == "aadhaar":
            from app.adapters.aadhaar_adapter import screen_aadhaar_file
            res = screen_aadhaar_file(sample_path)
        elif m["id"] == "passport":
            from app.adapters.passport_adapter import screen_passport_file
            res = screen_passport_file(sample_path)
        elif m["id"] == "visa":
            from app.adapters.visa_adapter import screen_visa_file
            res = screen_visa_file(sample_path)
        elif m["id"] == "dl":
            from app.adapters.driving_licence_adapter import screen_driving_licence_file
            res = screen_driving_licence_file(sample_path)
        elif m["id"] == "pan":
            from app.adapters.pan_adapter import screen_pan_file
            res = screen_pan_file(sample_path)

        # Check fields
        doc_type = getattr(res.document, "document_type", "Unknown")
        status = getattr(res.document, "processing_status", "unknown")
        err = getattr(res, "error", None)
        raw = getattr(res, "raw_response", None)
        evidence = getattr(res, "evidence", [])

        module_called = raw is not None or status != "error"
        ocr_executed = bool(raw) or len(evidence) > 0
        normalized = len(evidence) > 0

        print(f"  Doc Type: {doc_type}")
        print(f"  Processing Status: {status}")
        print(f"  Module Called: {module_called}")
        print(f"  Evidence Count: {len(evidence)}")
        if err:
            print(f"  Error Detail: {err}")

        results.append({
            "document": name,
            "port": port,
            "processing_status": status,
            "module_called": module_called,
            "ocr_executed": ocr_executed,
            "normalized": normalized,
            "evidence_count": len(evidence),
            "error": err
        })

    # Test full central DAKSH endpoint /api/screen-case
    print("\n=== 3. DAKSH CENTRAL ENDPOINT TEST (/api/screen-case) ===")
    try:
        files = {
            "aadhaar": ("01_AADHAAR_MATCH.jpg", open(SAMPLE_DIR / "01_AADHAAR_MATCH.jpg", "rb"), "image/jpeg"),
            "driving_licence": ("05_DL_PRIYA_VERMA.jpg", open(SAMPLE_DIR / "05_DL_PRIYA_VERMA.jpg", "rb"), "image/jpeg"),
            "pan": ("05_PAN_PRIYA_VERMA.jpg", open(SAMPLE_DIR / "05_PAN_PRIYA_VERMA.jpg", "rb"), "image/jpeg"),
            "passport": ("01_PASSPORT_MATCH.jpg", open(SAMPLE_DIR / "01_PASSPORT_MATCH.jpg", "rb"), "image/jpeg"),
            "visa": ("01_VISA_MATCH.jpg", open(SAMPLE_DIR / "01_VISA_MATCH.jpg", "rb"), "image/jpeg"),
        }
        r = requests.post("http://127.0.0.1:8000/api/screen-case", files=files, timeout=60.0)
        print(f"Central DAKSH /api/screen-case Status Code: {r.status_code}")
        if r.ok:
            data = r.json()
            print(f"Case ID: {data.get('case_id')}")
            print(f"Documents count: {len(data.get('documents', []))}")
            print(f"Evidence items count: {len(data.get('evidence', []))}")
            print(f"Contradictions count: {len(data.get('contradictions', []))}")
        else:
            print(f"DAKSH screen-case response: {r.text[:300]}")
    except Exception as e:
        print(f"DAKSH screen-case request failed: {e}")

    return results


if __name__ == "__main__":
    check_health()
    test_adapters_and_backend()
