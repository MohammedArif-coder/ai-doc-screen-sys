from app.passport.ocr import run_ocr


IMAGE_PATH = "app/passport/artifacts/mrz_crop.png"

print("Running MRZ-only OCR...")

results = run_ocr(IMAGE_PATH)

print("\nMRZ OCR RESULTS")
print("=" * 70)

for i, item in enumerate(results, start=1):
    print(f"\n{i}. {item['text']}")
    print(f"Confidence: {item['confidence']}")
    print(f"Box: {item['box']}")