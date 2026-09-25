from pathlib import Path
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


def analyze_image_quality(image_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError("Could not read image.")

    height, width = image.shape[:2]

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    sharpness = float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )

    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    resolution_ok = (
        width >= 700 and
        height >= 500
    )

    if sharpness >= 150:
        sharpness_status = "GOOD"
    elif sharpness >= 60:
        sharpness_status = "FAIR"
    else:
        sharpness_status = "POOR"

    if not resolution_ok:
        overall = "LOW"
    elif sharpness_status == "POOR":
        overall = "LOW"
    elif brightness < 45 or brightness > 220:
        overall = "FAIR"
    else:
        overall = "GOOD"

    warnings = []

    if not resolution_ok:
        warnings.append(
            "Image resolution is low."
        )

    if sharpness < 60:
        warnings.append(
            "Image is blurry."
        )

    if brightness < 45:
        warnings.append(
            "Image is dark."
        )

    if brightness > 220:
        warnings.append(
            "Image is overexposed."
        )

    return {
        "width": width,
        "height": height,
        "sharpness": round(sharpness, 2),
        "brightness": round(brightness, 2),
        "contrast": round(contrast, 2),
        "sharpness_status": sharpness_status,
        "overall": overall,
        "usable": (
            resolution_ok and
            sharpness_status != "POOR"
        ),
        "warnings": warnings
    }


def analyze_metadata(image_path):
    image_path = Path(image_path)

    result = {
        "format": None,
        "width": None,
        "height": None,
        "mode": None,
        "exif_present": False,
        "software": None,
        "camera_make": None,
        "camera_model": None,
        "datetime": None,
        "orientation": None
    }

    try:
        with Image.open(image_path) as image:

            result["format"] = image.format
            result["width"] = image.width
            result["height"] = image.height
            result["mode"] = image.mode

            exif = image.getexif()

            if exif:

                result["exif_present"] = True

                result["software"] = exif.get(305)
                result["camera_make"] = exif.get(271)
                result["camera_model"] = exif.get(272)
                result["datetime"] = exif.get(306)
                result["orientation"] = exif.get(274)

    except Exception as exc:

        result["error"] = str(exc)

    return result


def create_ela(
    image_path,
    output_path,
    annotated_heatmap_path,
    annotated_original_path,
    jpeg_quality=90
):
    image_path = Path(image_path)

    with Image.open(image_path) as image:

        image = image.convert("RGB")

        max_dimension = 1800

        scale = min(
            1.0,
            max_dimension /
            max(image.width, image.height)
        )

        if scale < 1.0:

            new_size = (
                int(image.width * scale),
                int(image.height * scale)
            )

            image = image.resize(
                new_size,
                Image.Resampling.LANCZOS
            )

        working_image = image.copy()

        buffer = BytesIO()

        working_image.save(
            buffer,
            format="JPEG",
            quality=jpeg_quality
        )

        buffer.seek(0)

        recompressed = Image.open(
            buffer
        ).convert("RGB")

        original = np.asarray(
            working_image
        ).astype(np.int16)

        compressed = np.asarray(
            recompressed
        ).astype(np.int16)

    diff = np.abs(
        original - compressed
    )

    diff_gray = np.mean(
        diff,
        axis=2
    )

    scale_factor = 10.0

    ela = np.clip(
        diff_gray * scale_factor,
        0,
        255
    ).astype(np.uint8)

    ela = cv2.GaussianBlur(
        ela,
        (5, 5),
        0
    )

    cv2.imwrite(
        str(output_path),
        ela
    )

    mean_value = float(
        np.mean(ela)
    )

    max_value = int(
        np.max(ela)
    )

    percentile_99 = float(
        np.percentile(
            ela,
            99
        )
    )

    threshold = max(
        40,
        int(percentile_99)
    )

    mask = np.where(
        ela >= threshold,
        255,
        0
    ).astype(np.uint8)

    kernel = np.ones(
        (5, 5),
        np.uint8
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    heatmap_height, heatmap_width = ela.shape

    regions = []

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        area = w * h

        if area < 300:
            continue

        regions.append({
            "x": x,
            "y": y,
            "width": w,
            "height": h,
            "area": area,
            "relative_x": round(
                x / heatmap_width,
                4
            ),
            "relative_y": round(
                y / heatmap_height,
                4
            )
        })

    regions.sort(
        key=lambda item: item["area"],
        reverse=True
    )

    regions = regions[:10]

    if mean_value < 8:
        anomaly_level = "LOW"
    elif mean_value < 18:
        anomaly_level = "MEDIUM"
    else:
        anomaly_level = "HIGH"

    # --------------------------------------------------
    # Annotated ELA heatmap
    # --------------------------------------------------

    ela_color = cv2.cvtColor(
        ela,
        cv2.COLOR_GRAY2BGR
    )

    for index, region in enumerate(
        regions,
        start=1
    ):

        x = region["x"]
        y = region["y"]
        w = region["width"]
        h = region["height"]

        cv2.rectangle(
            ela_color,
            (x, y),
            (x + w, y + h),
            (255, 255, 255),
            3
        )

        cv2.putText(
            ela_color,
            str(index),
            (x, max(25, y - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

    cv2.imwrite(
        str(annotated_heatmap_path),
        ela_color
    )

    # --------------------------------------------------
    # Annotated original passport
    # --------------------------------------------------

    original_image = cv2.imread(
        str(image_path)
    )

    if original_image is not None:

        original_height, original_width = (
            original_image.shape[:2]
        )

        scale_x = (
            original_width /
            heatmap_width
        )

        scale_y = (
            original_height /
            heatmap_height
        )

        for index, region in enumerate(
            regions,
            start=1
        ):

            x1 = int(
                region["x"] * scale_x
            )

            y1 = int(
                region["y"] * scale_y
            )

            x2 = int(
                (region["x"] +
                 region["width"]) * scale_x
            )

            y2 = int(
                (region["y"] +
                 region["height"]) * scale_y
            )

            cv2.rectangle(
                original_image,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                4
            )

            cv2.putText(
                original_image,
                f"ELA-{index}",
                (x1, max(35, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                3
            )

        cv2.imwrite(
            str(annotated_original_path),
            original_image
        )

    return {
        "mean": round(
            mean_value,
            2
        ),
        "max": max_value,
        "percentile_99": round(
            percentile_99,
            2
        ),
        "threshold": threshold,
        "anomaly_level": anomaly_level,
        "suspicious_regions": regions,
        "heatmap_width": heatmap_width,
        "heatmap_height": heatmap_height,
        "output_path": str(
            output_path
        ),
        "annotated_heatmap_path": str(
            annotated_heatmap_path
        ),
        "annotated_original_path": str(
            annotated_original_path
        )
    }


def run_forensics(
    image_path,
    ela_output_path
):

    image_path = Path(image_path)

    ela_output_path = Path(
        ela_output_path
    )

    annotated_heatmap_path = (
        ela_output_path.parent /
        "annotated_ela.png"
    )

    annotated_original_path = (
        ela_output_path.parent /
        "annotated_passport.png"
    )

    quality = analyze_image_quality(
        image_path
    )

    metadata = analyze_metadata(
        image_path
    )

    ela = create_ela(
        image_path,
        ela_output_path,
        annotated_heatmap_path,
        annotated_original_path
    )

    return {
        "image_quality": quality,
        "metadata": metadata,
        "ela": ela
    }