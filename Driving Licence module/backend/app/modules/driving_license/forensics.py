import cv2
import numpy as np
from pathlib import Path


# ============================================================
# BASIC IMAGE METRICS
# ============================================================

def calculate_blur_score(gray):
    return float(
        cv2.Laplacian(gray, cv2.CV_64F).var()
    )


def calculate_brightness(gray):
    return float(np.mean(gray))


def calculate_edge_ratio(gray):
    edges = cv2.Canny(gray, 100, 200)

    total_pixels = gray.shape[0] * gray.shape[1]

    if total_pixels == 0:
        return 0.0

    return float(
        np.count_nonzero(edges) / total_pixels
    )


def calculate_texture_ratio(gray):
    texture = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    total_pixels = gray.shape[0] * gray.shape[1]

    if total_pixels == 0:
        return 0.0

    return float(
        np.count_nonzero(
            np.abs(texture) > 20
        ) / total_pixels
    )


# ============================================================
# FACE REGION DETECTION
# ============================================================

def detect_face_regions(image):

    regions = []

    try:
        height, width = image.shape[:2]

        backend_dir = (
            Path(__file__).resolve().parents[3]
        )

        model_path = (
            backend_dir
            / "models"
            / "face_detection_yunet_2023mar.onnx"
        )

        if not model_path.exists():
            return regions

        detector = cv2.FaceDetectorYN.create(
            str(model_path),
            "",
            (width, height),
            0.8,
            0.3,
            5000
        )

        _, faces = detector.detect(image)

        if faces is None:
            return regions

        for face in faces:

            x = max(0, int(face[0]))
            y = max(0, int(face[1]))
            w = max(0, int(face[2]))
            h = max(0, int(face[3]))

            if w <= 0 or h <= 0:
                continue

            regions.append({
                "x": x,
                "y": y,
                "width": w,
                "height": h
            })

    except Exception:
        return []

    return regions


def is_inside_face_region(
    x,
    y,
    w,
    h,
    face_regions
):

    for face in face_regions:

        fx = face["x"]
        fy = face["y"]
        fw = face["width"]
        fh = face["height"]

        x1 = max(x, fx)
        y1 = max(y, fy)

        x2 = min(
            x + w,
            fx + fw
        )

        y2 = min(
            y + h,
            fy + fh
        )

        if x2 <= x1 or y2 <= y1:
            continue

        intersection = (
            (x2 - x1)
            * (y2 - y1)
        )

        candidate_area = w * h

        if candidate_area <= 0:
            continue

        overlap_ratio = (
            intersection
            / candidate_area
        )

        if overlap_ratio >= 0.30:
            return True

    return False


# ============================================================
# BLOCK METRICS
# ============================================================

def calculate_block_metrics(block):

    gray = cv2.cvtColor(
        block,
        cv2.COLOR_BGR2GRAY
    )

    edges = cv2.Canny(
        gray,
        60,
        140
    )

    edge_density = (
        np.count_nonzero(edges)
        / block.size
    )

    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    texture_strength = float(
        np.mean(
            np.abs(laplacian)
        )
    )

    brightness = float(
        np.mean(gray)
    )

    brightness_std = float(
        np.std(gray)
    )

    # Colour-channel difference.
    # Edited regions can sometimes have different
    # colour/noise characteristics from nearby regions.
    b, g, r = cv2.split(block)

    colour_difference = float(
        np.mean(
            np.abs(
                r.astype(np.float32)
                - g.astype(np.float32)
            )
        )
        +
        np.mean(
            np.abs(
                g.astype(np.float32)
                - b.astype(np.float32)
            )
        )
    )

    return {
        "edge_density": edge_density,
        "texture_strength": texture_strength,
        "brightness": brightness,
        "brightness_std": brightness_std,
        "colour_difference": colour_difference
    }


# ============================================================
# LOCALIZED IMAGE ANALYSIS
# ============================================================

def calculate_local_inconsistency(
    image,
    face_regions
):
    """
    Detect localized image regions whose visual
    characteristics differ significantly from the
    surrounding document.

    This is an anomaly detector.
    It does NOT prove that a document is forged.
    """

    height, width = image.shape[:2]

    if width < 300 or height < 200:
        return []

    block_size = 40

    values = []

    for y in range(
        0,
        height - block_size + 1,
        block_size
    ):

        for x in range(
            0,
            width - block_size + 1,
            block_size
        ):

            if is_inside_face_region(
                x,
                y,
                block_size,
                block_size,
                face_regions
            ):
                continue

            block = image[
                y:y + block_size,
                x:x + block_size
            ]

            if block.size == 0:
                continue

            metrics = calculate_block_metrics(
                block
            )

            values.append({
                "x": x,
                "y": y,
                "width": block_size,
                "height": block_size,
                **metrics
            })

    if len(values) < 8:
        return []

    # --------------------------------------------------------
    # Calculate robust medians
    # --------------------------------------------------------

    edge_values = np.array([
        item["edge_density"]
        for item in values
    ])

    texture_values = np.array([
        item["texture_strength"]
        for item in values
    ])

    brightness_values = np.array([
        item["brightness"]
        for item in values
    ])

    brightness_std_values = np.array([
        item["brightness_std"]
        for item in values
    ])

    colour_values = np.array([
        item["colour_difference"]
        for item in values
    ])

    edge_median = float(
        np.median(edge_values)
    )

    texture_median = float(
        np.median(texture_values)
    )

    brightness_median = float(
        np.median(brightness_values)
    )

    brightness_std_median = float(
        np.median(brightness_std_values)
    )

    colour_median = float(
        np.median(colour_values)
    )

    # --------------------------------------------------------
    # Robust deviation thresholds
    # --------------------------------------------------------

    edge_mad = float(
        np.median(
            np.abs(
                edge_values
                - edge_median
            )
        )
    )

    texture_mad = float(
        np.median(
            np.abs(
                texture_values
                - texture_median
            )
        )
    )

    brightness_mad = float(
        np.median(
            np.abs(
                brightness_values
                - brightness_median
            )
        )
    )

    brightness_std_mad = float(
        np.median(
            np.abs(
                brightness_std_values
                - brightness_std_median
            )
        )
    )

    colour_mad = float(
        np.median(
            np.abs(
                colour_values
                - colour_median
            )
        )
    )

    edge_threshold = max(
        edge_mad * 5.0,
        0.10
    )

    texture_threshold = max(
        texture_mad * 5.0,
        10.0
    )

    brightness_threshold = max(
        brightness_mad * 5.0,
        30.0
    )

    brightness_std_threshold = max(
        brightness_std_mad * 5.0,
        20.0
    )

    colour_threshold = max(
        colour_mad * 5.0,
        20.0
    )

    candidates = []

    # --------------------------------------------------------
    # Find abnormal blocks
    # --------------------------------------------------------

    for item in values:

        edge_difference = abs(
            item["edge_density"]
            - edge_median
        )

        texture_difference = abs(
            item["texture_strength"]
            - texture_median
        )

        brightness_difference = abs(
            item["brightness"]
            - brightness_median
        )

        brightness_std_difference = abs(
            item["brightness_std"]
            - brightness_std_median
        )

        colour_difference = abs(
            item["colour_difference"]
            - colour_median
        )

        edge_anomaly = (
            edge_difference
            > edge_threshold
        )

        texture_anomaly = (
            texture_difference
            > texture_threshold
        )

        brightness_anomaly = (
            brightness_difference
            > brightness_threshold
        )

        contrast_anomaly = (
            brightness_std_difference
            > brightness_std_threshold
        )

        colour_anomaly = (
            colour_difference
            > colour_threshold
        )

        # Count independent anomaly signals.
        anomaly_count = sum([
            edge_anomaly,
            texture_anomaly,
            brightness_anomaly,
            contrast_anomaly,
            colour_anomaly
        ])

        # Require at least three independent signals.
        if anomaly_count >= 3:

            candidates.append({
                "x": item["x"],
                "y": item["y"],
                "width": item["width"],
                "height": item["height"],
                "anomaly_score": anomaly_count,
                "edge_difference": round(
                    edge_difference,
                    4
                ),
                "texture_difference": round(
                    texture_difference,
                    2
                ),
                "brightness_difference": round(
                    brightness_difference,
                    2
                ),
                "colour_difference": round(
                    colour_difference,
                    2
                )
            })

    # --------------------------------------------------------
    # Merge nearby suspicious blocks
    # --------------------------------------------------------

    merged = []

    for candidate in candidates:

        merged_into_existing = False

        for region in merged:

            rx = region["x"]
            ry = region["y"]
            rw = region["width"]
            rh = region["height"]

            cx = candidate["x"]
            cy = candidate["y"]
            cw = candidate["width"]
            ch = candidate["height"]

            horizontal_gap = max(
                0,
                max(rx, cx)
                - min(rx + rw, cx + cw)
            )

            vertical_gap = max(
                0,
                max(ry, cy)
                - min(ry + rh, cy + ch)
            )

            if (
                horizontal_gap <= block_size
                and vertical_gap <= block_size
            ):

                new_x = min(
                    rx,
                    cx
                )

                new_y = min(
                    ry,
                    cy
                )

                new_right = max(
                    rx + rw,
                    cx + cw
                )

                new_bottom = max(
                    ry + rh,
                    cy + ch
                )

                region["x"] = new_x
                region["y"] = new_y
                region["width"] = (
                    new_right - new_x
                )
                region["height"] = (
                    new_bottom - new_y
                )

                region["anomaly_score"] = max(
                    region.get(
                        "anomaly_score",
                        0
                    ),
                    candidate.get(
                        "anomaly_score",
                        0
                    )
                )

                merged_into_existing = True
                break

        if not merged_into_existing:

            merged.append({
                "x": candidate["x"],
                "y": candidate["y"],
                "width": candidate["width"],
                "height": candidate["height"],
                "anomaly_score": candidate[
                    "anomaly_score"
                ]
            })

    return merged[:10]


# ============================================================
# QUALITY ANALYSIS
# ============================================================

def analyze_quality(
    width,
    height,
    blur_score,
    brightness
):

    warnings = []

    if width < 600 or height < 400:

        warnings.append({
            "type": "LOW_RESOLUTION",
            "severity": "MEDIUM",
            "message": (
                "Document image resolution is low and "
                "may affect verification."
            )
        })

    if blur_score < 100:

        warnings.append({
            "type": "BLUR",
            "severity": "MEDIUM",
            "message": (
                "Document image appears blurred and "
                "may affect OCR or forensic analysis."
            )
        })

    if brightness < 45:

        warnings.append({
            "type": "LOW_BRIGHTNESS",
            "severity": "MEDIUM",
            "message": (
                "Document image is unusually dark."
            )
        })

    elif brightness > 245:

        warnings.append({
            "type": "HIGH_BRIGHTNESS",
            "severity": "MEDIUM",
            "message": (
                "Document image is unusually bright "
                "or overexposed."
            )
        })

    return warnings


# ============================================================
# MAIN FORENSIC ANALYSIS
# ============================================================

def analyze_forensics(image_path: str):

    image = cv2.imread(
        image_path
    )

    if image is None:

        return {
            "status": "ERROR",
            "quality_status": "REVIEW",
            "quality_warning_count": 1,
            "quality_warnings": [
                {
                    "type": "IMAGE_READ_ERROR",
                    "severity": "HIGH",
                    "message": (
                        "Unable to read the document image."
                    )
                }
            ],
            "image_width": 0,
            "image_height": 0,
            "blur_score": 0.0,
            "brightness": 0.0,
            "edge_ratio": 0.0,
            "texture_ratio": 0.0,
            "brightness_std": 0.0,
            "face_regions_excluded": [],
            "suspicious_regions": [],
            "photo_anomalies": [],
            "tampering_signals": [],
            "signals": []
        }

    height, width = image.shape[:2]

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blur_score = calculate_blur_score(
        gray
    )

    brightness = calculate_brightness(
        gray
    )

    edge_ratio = calculate_edge_ratio(
        gray
    )

    texture_ratio = calculate_texture_ratio(
        gray
    )

    brightness_std = float(
        np.std(gray)
    )

    # --------------------------------------------------------
    # Quality
    # --------------------------------------------------------

    quality_warnings = analyze_quality(
        width,
        height,
        blur_score,
        brightness
    )

    quality_status = (
        "REVIEW"
        if quality_warnings
        else "NORMAL"
    )

    # --------------------------------------------------------
    # Face regions are excluded from tampering analysis
    # --------------------------------------------------------

    face_regions = detect_face_regions(
        image
    )

    # --------------------------------------------------------
    # Localized forensic analysis
    # --------------------------------------------------------

    suspicious_regions = (
        calculate_local_inconsistency(
            image,
            face_regions
        )
    )

    tampering_signals = []

    # --------------------------------------------------------
    # Only create a tampering signal when there is
    # meaningful localized evidence.
    # --------------------------------------------------------

    if len(suspicious_regions) >= 1:

        tampering_signals.append({
            "type": "LOCAL_IMAGE_INCONSISTENCY",
            "severity": "MEDIUM",
            "message": (
                "A localized document region shows "
                "visual characteristics that differ "
                "substantially from surrounding regions. "
                "Manual review is recommended."
            )
        })

    if len(suspicious_regions) >= 3:

        tampering_signals.append({
            "type": "MULTIPLE_SUSPICIOUS_REGIONS",
            "severity": "MEDIUM",
            "message": (
                "Multiple localized regions show "
                "unusual visual characteristics. "
                "Possible editing should be reviewed."
            )
        })

    # --------------------------------------------------------
    # Final status
    # --------------------------------------------------------

    if tampering_signals:
        status = "REVIEW"
    else:
        status = "NORMAL"

    return {
        "status": status,

        "quality_status": quality_status,

        "quality_warning_count": len(
            quality_warnings
        ),

        "quality_warnings": quality_warnings,

        "image_width": width,

        "image_height": height,

        "blur_score": round(
            blur_score,
            2
        ),

        "brightness": round(
            brightness,
            2
        ),

        "edge_ratio": round(
            edge_ratio,
            4
        ),

        "texture_ratio": round(
            texture_ratio,
            4
        ),

        "brightness_std": round(
            brightness_std,
            2
        ),

        "face_regions_excluded": face_regions,

        "suspicious_regions": suspicious_regions,

        "photo_anomalies": [],

        "tampering_signals": tampering_signals,

        "signals": quality_warnings
    }