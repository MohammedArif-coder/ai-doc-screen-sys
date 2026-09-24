import cv2
import pytesseract

from pytesseract import Output


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def preprocess_image(image):
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.resize(
        gray,
        None,
        fx=2,
        fy=2,
        interpolation=cv2.INTER_CUBIC
    )

    processed = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return processed


def extract_text(image_path: str) -> str:

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            "Unable to read the document image."
        )

    processed = preprocess_image(image)

    text = pytesseract.image_to_string(
        processed,
        config="--psm 6"
    )

    return text.strip()


def extract_ocr_with_confidence(
    image_path: str
) -> dict:

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            "Unable to read the document image."
        )

    processed = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed,
        config="--psm 6",
        output_type=Output.DICT
    )

    words = []
    confidences = []

    for i in range(len(data["text"])):

        word = data["text"][i].strip()
        confidence = data["conf"][i]

        if not word:
            continue

        try:
            confidence = float(confidence)
        except ValueError:
            continue

        if confidence < 0:
            continue

        words.append(word)
        confidences.append(confidence)

    if confidences:
        average_confidence = (
            sum(confidences)
            / len(confidences)
        )
    else:
        average_confidence = 0.0

    return {
        "text": " ".join(words),
        "average_confidence": round(
            average_confidence,
            2
        ),
        "word_count": len(words)
    }