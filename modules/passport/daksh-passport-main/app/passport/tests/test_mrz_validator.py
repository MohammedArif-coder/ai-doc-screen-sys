from app.passport.ocr import run_ocr
from app.passport.mrz import find_mrz_candidates
from app.passport.mrz_validator import validate_mrz


IMAGE_PATH = "app/passport/artifacts/processed.jpg"

print("Running OCR...")

ocr_results = run_ocr(IMAGE_PATH)

mrz_candidates = find_mrz_candidates(ocr_results)

if len(mrz_candidates) < 2:
    print("MRZ not found")
    exit()

line1 = mrz_candidates[0]["text"]
line2 = mrz_candidates[1]["text"]

print("\nMRZ LINE 1:")
print(line1)

print("\nMRZ LINE 2:")
print(line2)

result = validate_mrz(line1, line2)

print("\nMRZ VALIDATION")
print("=" * 60)

print("Line 1 length:", result["line1_length"])
print("Line 2 length:", result["line2_length"])

for field, check in result["checks"].items():
    status = "PASS" if check["valid"] else "FAIL"

    print(f"\n{field}: {status}")
    print("Expected:", check["expected"])
    print("Calculated:", check["calculated"])