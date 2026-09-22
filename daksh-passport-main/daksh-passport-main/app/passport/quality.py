import cv2


def analyze_quality(image):
    height, width = image.shape[:2]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    sharpness_score = cv2.Laplacian(gray, cv2.CV_64F).var()

    if width >= 1200 and height >= 800:
        resolution_status = "GOOD"
    else:
        resolution_status = "LOW"

    if sharpness_score >= 200:
        blur_status = "GOOD"
    elif sharpness_score >= 80:
        blur_status = "MODERATE"
    else:
        blur_status = "POOR"

    usable = (
        resolution_status != "LOW"
        and blur_status != "POOR"
    )

    return {
    "width": width,
    "height": height,
    "resolution_status": resolution_status,
    "sharpness_score": round(float(sharpness_score), 2),
    "blur_status": blur_status,
    "usable": usable,
    "warning": (
        "Image is moderately blurry"
        if blur_status == "MODERATE"
        else "Image is severely blurry"
        if blur_status == "POOR"
        else None
    )
}