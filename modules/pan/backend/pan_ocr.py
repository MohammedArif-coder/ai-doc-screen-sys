import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


import os
import shutil

tesseract_env = os.environ.get("TESSERACT_CMD")
if tesseract_env and os.path.exists(tesseract_env):
    pytesseract.pytesseract.tesseract_cmd = tesseract_env
elif os.path.exists(r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
elif shutil.which("tesseract"):
    pytesseract.pytesseract.tesseract_cmd = shutil.which("tesseract")
else:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def preprocess_image(image):
    """
    Preprocess the PAN image for better OCR.
    """

    # Convert to grayscale
    image = image.convert("L")

    # Increase contrast
    contrast = ImageEnhance.Contrast(image)
    image = contrast.enhance(2.0)

    # Sharpen
    image = image.filter(
        ImageFilter.SHARPEN
    )

    # Resize image
    width, height = image.size

    image = image.resize(
        (width * 3, height * 3)
    )

    return image


def extract_text(image_path):

    # Open image
    image = Image.open(image_path)

    # Preprocess
    processed_image = preprocess_image(image)

    # OCR configuration
    config = "--psm 6"

    # Extract text
    text = pytesseract.image_to_string(
        processed_image,
        config=config
    )

    return text


if __name__ == "__main__":

    image_path = "input/dummy_pan.png"

    text = extract_text(image_path)

    print("----- OCR OUTPUT -----")
    print(text)