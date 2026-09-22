from app.passport.ocr import run_ocr


IMAGE_PATH = "app/passport/samples/test.jpg"


results = run_ocr(IMAGE_PATH)


print("\nOCR RESULTS")
print("=" * 60)

if not results:
    print("No text detected.")
else:
    for i, item in enumerate(results, start=1):
        print(f"\n{i}. {item['text']}")
        print(f"   Confidence: {item['confidence']}")
        print(f"   Box: {item['box']}")