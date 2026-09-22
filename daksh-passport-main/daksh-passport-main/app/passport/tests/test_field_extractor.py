from app.passport.ocr import run_ocr
from app.passport.field_extractor import extract_visual_fields


IMAGE_PATH = "app/passport/artifacts/processed.jpg"

print("Running OCR...")

ocr_results = run_ocr(IMAGE_PATH)

fields = extract_visual_fields(ocr_results)

print("\nEXTRACTED VISUAL FIELDS")
print("=" * 60)

for key, value in fields.items():
    print(f"{key}: {value}")