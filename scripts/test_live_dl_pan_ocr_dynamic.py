"""Test live dynamic OCR extraction on 05_DL_PRIYA_VERMA.jpg and 05_PAN_PRIYA_VERMA.jpg."""

from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "daksh-backend"))

from app.adapters.driving_licence_adapter import screen_driving_licence_file
from app.adapters.pan_adapter import screen_pan_file

def run():
    dl_res = screen_driving_licence_file("sample_documents/05_DL_PRIYA_VERMA.jpg")
    pan_res = screen_pan_file("sample_documents/05_PAN_PRIYA_VERMA.jpg")

    print("=== LIVE DRIVING LICENCE EXTRACTION FOR PRIYA VERMA ===")
    for ev in dl_res.evidence:
        print(f"  {ev.field:<25}: {ev.value}")

    print("\n=== LIVE PAN CARD EXTRACTION FOR PRIYA VERMA ===")
    for ev in pan_res.evidence:
        print(f"  {ev.field:<25}: {ev.value}")

if __name__ == "__main__":
    run()
