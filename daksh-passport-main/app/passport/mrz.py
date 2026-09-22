import re


MRZ_ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<")


def normalize_mrz(text):
    text = text.upper().strip()

    # Common OCR correction
    text = text.replace(" ", "")

    # Keep only valid MRZ characters
    text = "".join(
        c for c in text
        if c in MRZ_ALLOWED
    )

    return text


def is_mrz_candidate(text):
    text = normalize_mrz(text)

    if len(text) < 30:
        return False

    # MRZ normally contains many '<' filler characters
    if "<" not in text:
        return False

    alphanumeric = sum(c.isalnum() for c in text)

    return alphanumeric >= 15


def find_mrz_candidates(ocr_results):

    candidates = []

    for item in ocr_results:

        text = normalize_mrz(item["text"])

        if is_mrz_candidate(text):

            candidates.append({
                "text": text,
                "confidence": item["confidence"],
                "box": item["box"]
            })

    return candidates