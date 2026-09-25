from app.passport.ocr import run_ocr
from app.passport.mrz import find_mrz_candidates


IMAGE_PATH = "app/passport/artifacts/processed.jpg"


print("Running OCR...")

ocr_results = run_ocr(IMAGE_PATH)

print("OCR completed.")
print()


mrz_candidates = find_mrz_candidates(ocr_results)


print("MRZ CANDIDATES")
print("=" * 70)


for i, item in enumerate(mrz_candidates, start=1):

    print(f"\n{i}. {item['text']}")
    print(f"Confidence: {item['confidence']}")
    print(f"Box: {item['box']}")