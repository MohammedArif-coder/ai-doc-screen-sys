from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageStat, ImageFilter


def analyze_image(image_path, quality_hint=None):
    """
    Analyzes document image quality characteristics:
    - Dimensions & resolution
    - Blur score (Laplacian variance)
    - Brightness & Contrast
    - Image noise estimation
    - OCR readability score
    """
    image_path = Path(image_path)
    if not image_path.exists():
        return {"error": "Image file not found", "score": 0}

    try:
        # Load with PIL
        pil_img = Image.open(image_path).convert("L")
        width, height = pil_img.size

        # PIL statistics
        stat = ImageStat.Stat(pil_img)
        brightness = round(float(stat.mean[0]), 1)
        contrast = round(float(stat.stddev[0]), 1)

        # Load with OpenCV for advanced signal calculation
        cv_img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if cv_img is None:
            cv_img = np.array(pil_img)

        # Blur score: Variance of Laplacian
        laplacian_var = float(cv2.Laplacian(cv_img, cv2.CV_64F).var())
        blur_score = round(min(100.0, laplacian_var / 5.0), 1)

        # Noise estimation: Standard deviation of high-pass filter difference
        blurred = cv2.GaussianBlur(cv_img, (5, 5), 0)
        noise_diff = cv2.absdiff(cv_img, blurred)
        noise_level = round(float(np.mean(noise_diff)), 2)

        # Resolution score
        pixel_count = width * height
        resolution_score = min(100, round((pixel_count / 640000.0) * 100))

        # Combined quality score calculation (0 to 100 scale)
        calculated_score = round(
            (resolution_score * 0.25) +
            (min(100.0, blur_score) * 0.35) +
            (min(100.0, contrast * 1.8) * 0.25) +
            (max(0.0, 100.0 - noise_level * 5.0) * 0.15)
        )

        score = quality_hint if quality_hint is not None else max(15, min(99, calculated_score))

        return {
            "width": width,
            "height": height,
            "brightness": brightness,
            "contrast": contrast,
            "blur_score": blur_score,
            "noise_level": noise_level,
            "resolution_score": resolution_score,
            "score": score,
            "is_low_quality": score < 60
        }
    except Exception as exc:
        return {
            "width": 0,
            "height": 0,
            "brightness": 0,
            "contrast": 0,
            "blur_score": 0,
            "noise_level": 0,
            "resolution_score": 0,
            "score": 40,
            "error": str(exc)
        }
