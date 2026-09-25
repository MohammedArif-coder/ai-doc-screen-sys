from app.passport.ocr import run_ocr
from app.passport.mrz import find_mrz_candidates
from app.passport.mrz_parser import parse_td3

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

data = parse_td3(line1, line2)

print("\nPARSED MRZ")
print("=" * 50)

for key, value in data.items():
    print(f"{key}: {value}")