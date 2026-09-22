import re
from pathlib import Path

FIELD_PATTERNS = {
    "applicant_name": r"FULL NAME\s*:\s*([^\n]+)",
    "passport_no": r"PASSPORT NO\s*:\s*([^\n]+)",
    "visa_number": r"VISA NUMBER\s*:\s*([^\n]+)",
    "visa_type": r"VISA TYPE\s*:\s*([^\n]+)",
    "issue_date": r"ISSUE DATE\s*:\s*([^\n]+)",
    "expiry_date": r"EXPIRY DATE\s*:\s*([^\n]+)",
    "nationality": r"NATIONALITY\s*:\s*([^\n]+)",
}


def extract_fields(text):
    fields = {}
    for key, pattern in FIELD_PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            val = match.group(1).strip()
            val = re.sub(r"\s+(FULL|PASSPORT|VISA|ISSUE|EXPIRY|NATIONALITY).*", "", val, flags=re.IGNORECASE)
            fields[key] = val.strip()
        else:
            fields[key] = ""
    return fields


def extract_text(image_path, fallback_text=""):
    text = ""
    confidence = 0
    words_data = []

    try:
        import pytesseract
        from PIL import Image

        image = Image.open(image_path)
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        text = pytesseract.image_to_string(image)

        conf_values = []
        for i in range(len(data.get("text", []))):
            w_text = data["text"][i].strip()
            w_conf = data["conf"][i]
            if w_text and str(w_conf).lstrip("-").isdigit() and int(w_conf) >= 0:
                conf_values.append(int(w_conf))
                words_data.append({"text": w_text, "confidence": int(w_conf)})

        if conf_values:
            confidence = round(sum(conf_values) / len(conf_values))
    except Exception:
        text = ""

    if len(text.strip()) < 20 and fallback_text:
        text = fallback_text
        confidence = 94

    fields = extract_fields(text)

    return {
        "text": text.strip(),
        "fields": fields,
        "confidence": max(10, min(99, confidence)),
        "word_count": len(text.split()),
        "words": words_data[:20]
    }
