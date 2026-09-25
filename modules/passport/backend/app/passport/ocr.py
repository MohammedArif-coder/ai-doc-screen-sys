import os

# Workaround for PaddlePaddle 3.x CPU + oneDNN PIR issue
os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR


ocr_engine = PaddleOCR(
    lang="en",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    enable_mkldnn=False
)


def run_ocr(image_path):
    results = ocr_engine.predict(image_path)

    detections = []

    for result in results:
        data = result.json

        if not data:
            continue

        res = data.get("res", {})

        texts = res.get("rec_texts", [])
        scores = res.get("rec_scores", [])
        boxes = res.get("rec_polys", [])

        for text, score, box in zip(texts, scores, boxes):
            detections.append({
                "text": text,
                "confidence": round(float(score), 4),
                "box": box.tolist() if hasattr(box, "tolist") else box
            })

    return detections