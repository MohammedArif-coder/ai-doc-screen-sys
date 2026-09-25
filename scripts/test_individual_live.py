import sys
import json
import requests
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = ROOT_DIR / "sample_documents"
sys.path.insert(0, str(ROOT_DIR / "daksh-backend"))

def test_module(name, sample_file, adapter_mod, adapter_fn):
    sample_path = SAMPLE_DIR / sample_file
    print(f"\n--- Testing {name} ({sample_file}) ---", flush=True)
    if not sample_path.exists():
        print(f"File not found: {sample_path}", flush=True)
        return
    mod = __import__(f"app.adapters.{adapter_mod}", fromlist=[adapter_fn])
    fn = getattr(mod, adapter_fn)
    res = fn(sample_path)
    print(f"Document Type: {getattr(res.document, 'document_type', None)}", flush=True)
    print(f"Processing Status: {getattr(res.document, 'processing_status', None)}", flush=True)
    print(f"Evidence Count: {len(getattr(res, 'evidence', []))}", flush=True)
    print(f"Error: {getattr(res, 'error', None)}", flush=True)
    if getattr(res, "evidence", None):
        print("Sample Evidence Items:", flush=True)
        for ev in res.evidence[:4]:
            print(f"  - [{ev.evidence_type.value}] {ev.field}: {ev.value}", flush=True)

if __name__ == "__main__":
    test_module("Aadhaar", "01_AADHAAR_MATCH.jpg", "aadhaar_adapter", "screen_aadhaar_file")
    test_module("Driving Licence", "05_DL_PRIYA_VERMA.jpg", "driving_licence_adapter", "screen_driving_licence_file")
    test_module("PAN", "05_PAN_PRIYA_VERMA.jpg", "pan_adapter", "screen_pan_file")
    test_module("Passport", "01_PASSPORT_MATCH.jpg", "passport_adapter", "screen_passport_file")
    test_module("Visa", "01_VISA_MATCH.jpg", "visa_adapter", "screen_visa_file")
