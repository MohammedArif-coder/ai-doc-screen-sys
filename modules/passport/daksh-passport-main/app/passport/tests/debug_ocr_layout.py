from app.passport.ocr import run_ocr


IMAGE_PATH = "app/passport/artifacts/processed.jpg"

results = run_ocr(IMAGE_PATH)

print("OCR LAYOUT")
print("=" * 100)

items = []

for item in results:
    text = str(item["text"]).strip()

    if not text:
        continue

    box = item["box"]

    xs = [p[0] for p in box]
    ys = [p[1] for p in box]

    left = min(xs)
    top = min(ys)
    right = max(xs)
    bottom = max(ys)

    items.append({
        "text": text,
        "left": left,
        "top": top,
        "right": right,
        "bottom": bottom
    })

# Sort by vertical position, then horizontal position
items.sort(key=lambda x: (x["top"], x["left"]))

for i, item in enumerate(items, start=1):
    print(
        f"{i:02d} | "
        f"{item['text']:<55} | "
        f"x={item['left']:<4}-{item['right']:<4} "
        f"y={item['top']:<4}-{item['bottom']:<4}"
    )