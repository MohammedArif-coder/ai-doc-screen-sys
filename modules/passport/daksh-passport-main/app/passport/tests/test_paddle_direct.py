import os

os.environ["FLAGS_enable_pir_api"] = "0"

from paddleocr import PaddleOCR


IMAGE_PATH = "app/passport/artifacts/processed.jpg"

print("Creating lightweight OCR engine...")

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",

    lang="en",

    device="cpu",
    cpu_threads=8,
    enable_mkldnn=False,

    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,

    text_det_limit_side_len=1280,
    text_det_limit_type="max"
)

print("OCR engine created.")
print("Starting prediction...")

results = ocr.predict(IMAGE_PATH)

print("Prediction completed.")
print("Number of results:", len(results))

for i, result in enumerate(results, start=1):
    print(f"\n========== RESULT {i} ==========")
    result.print()