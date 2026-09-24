"""Test PaddleOCR dynamic extraction for DL and PAN."""

import re
import sys
from pathlib import Path

sys.path.insert(0, r"c:\Users\arifi\OneDrive\Desktop\SIH 2026\DAKSH\daksh-passport-main")
from app.passport.ocr import run_ocr

def extract_dl_from_image(image_path):
    lines = [item["text"].strip() for item in run_ocr(image_path)]
    fields = {}
    
    for i, line in enumerate(lines):
        # DL Number match
        dl_match = re.search(r"[A-Z]{2}[0-9]{2}[0-9A-Z]{9,11}", line.replace(" ", "").upper())
        if dl_match and "dl_number" not in fields:
            fields["dl_number"] = dl_match.group(0)
            
        # Name
        if ("Name:" in line or line.upper() == "NAME") and i + 1 < len(lines):
            next_val = lines[i + 1]
            if not any(k in next_val for k in ["DOB", "PHOTO", "Address", "Authority"]):
                fields["name"] = next_val.replace(":", "").strip()
                
        # DOB
        if "DOB" in line.upper():
            date_match = re.search(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", line)
            if date_match:
                fields["dob"] = date_match.group(0)
            elif i + 1 < len(lines):
                next_date = re.search(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", lines[i + 1])
                if next_date:
                    fields["dob"] = next_date.group(0)
                    
        # Authority
        if "RTO" in line.upper():
            fields["issuing_authority"] = line.replace("Authority.", "").strip()
            
    return fields

def extract_pan_from_image(image_path):
    lines = [item["text"].strip() for item in run_ocr(image_path)]
    fields = {}
    
    for i, line in enumerate(lines):
        # PAN Number match
        pan_match = re.search(r"[A-Z]{5}[0-9]{4}[A-Z]{1}", line.replace(" ", "").upper())
        if pan_match and "pan_number" not in fields:
            fields["pan_number"] = pan_match.group(0)
            
        # Name
        if ("Name:" in line or line.upper() == "NAME") and "Father" not in line and i + 1 < len(lines):
            next_val = lines[i + 1]
            if not any(k in next_val for k in ["DOB", "PHOTO", "Father", "INCOME"]):
                fields["name"] = next_val.replace(":", "").strip()
                
        # Father Name
        if "Father" in line and i + 1 < len(lines):
            fields["father_name"] = lines[i + 1].replace(":", "").strip()
            
        # DOB
        if "DOB" in line.upper():
            date_match = re.search(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", line)
            if date_match:
                fields["dob"] = date_match.group(0)
            elif i + 1 < len(lines):
                next_date = re.search(r"\d{2}/\d{2}/\d{4}|\d{4}-\d{2}-\d{2}", lines[i + 1])
                if next_date:
                    fields["dob"] = next_date.group(0)
                    
    return fields

if __name__ == "__main__":
    print("EXTRACTED DL:", extract_dl_from_image("sample_documents/05_DL_PRIYA_VERMA.jpg"))
    print("EXTRACTED PAN:", extract_pan_from_image("sample_documents/05_PAN_PRIYA_VERMA.jpg"))
