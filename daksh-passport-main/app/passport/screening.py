from pathlib import Path

import cv2

from app.passport.ocr import run_ocr
from app.passport.field_extractor import extract_visual_fields
from app.passport.mrz import find_mrz_candidates
from app.passport.mrz_parser import parse_td3
from app.passport.mrz_validator import validate_mrz
from app.passport.consistency import compare_passport_fields
from app.passport.forensics import run_forensics


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

ARTIFACTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def preprocess_image(image_path, output_path):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            "Could not read the uploaded image."
        )

    height, width = image.shape[:2]

    target_height = 2000

    if height != target_height:

        scale = target_height / height

        new_width = int(width * scale)

        image = cv2.resize(
            image,
            (new_width, target_height),
            interpolation=cv2.INTER_CUBIC
        )

    success = cv2.imwrite(
        str(output_path),
        image
    )

    if not success:
        raise ValueError(
            "Could not save processed image."
        )

    return output_path


def crop_mrz_from_candidates(
    image_path,
    candidates,
    output_path
):
    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(
            "Could not read processed image."
        )

    if len(candidates) < 2:
        raise ValueError(
            "Two MRZ lines were not detected."
        )

    points = []

    for candidate in candidates[:2]:

        for point in candidate["box"]:
            points.append(point)

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    padding_x = 30
    padding_y = 40

    x1 = max(
        0,
        int(min(xs) - padding_x)
    )

    y1 = max(
        0,
        int(min(ys) - padding_y)
    )

    x2 = min(
        image.shape[1],
        int(max(xs) + padding_x)
    )

    y2 = min(
        image.shape[0],
        int(max(ys) + padding_y)
    )

    if x2 <= x1 or y2 <= y1:
        raise ValueError(
            "MRZ crop has invalid dimensions."
        )

    mrz = image[
        y1:y2,
        x1:x2
    ]

    if mrz.size == 0:
        raise ValueError(
            "MRZ crop is empty."
        )

    mrz = cv2.resize(
        mrz,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    gray = cv2.cvtColor(
        mrz,
        cv2.COLOR_BGR2GRAY
    )

    gray = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    success = cv2.imwrite(
        str(output_path),
        gray
    )

    if not success:
        raise ValueError(
            "Could not save MRZ crop."
        )

    return output_path


def screen_passport(image_path):

    image_path = Path(image_path)

    processed_path = (
        ARTIFACTS_DIR /
        "api_processed.jpg"
    )

    mrz_path = (
        ARTIFACTS_DIR /
        "api_mrz_crop.png"
    )

    ela_path = (
        ARTIFACTS_DIR /
        "api_ela_heatmap.png"
    )

    # --------------------------------------------------
    # 1. FORENSICS ON ORIGINAL IMAGE
    # --------------------------------------------------

    forensics = run_forensics(
        str(image_path),
        str(ela_path)
    )

    # --------------------------------------------------
    # 2. PREPROCESS FOR OCR
    # --------------------------------------------------

    preprocess_image(
        image_path,
        processed_path
    )

    # --------------------------------------------------
    # 3. FULL PAGE OCR
    # --------------------------------------------------

    ocr_results = run_ocr(
        str(processed_path)
    )

    # --------------------------------------------------
    # 4. VISUAL FIELDS
    # --------------------------------------------------

    visual_fields = extract_visual_fields(
        ocr_results
    )

    # --------------------------------------------------
    # 5. FIND MRZ
    # --------------------------------------------------

    mrz_candidates = find_mrz_candidates(
        ocr_results
    )

    mrz_candidates.sort(
        key=lambda item: min(
            point[1]
            for point in item["box"]
        )
    )

    if len(mrz_candidates) < 2:

        return {
            "status": "manual_review",
            "reason": "Could not detect two MRZ lines.",
            "visual_fields": visual_fields,
            "mrz": None,
            "forensics": forensics
        }

    # --------------------------------------------------
    # 6. DYNAMIC MRZ CROP
    # --------------------------------------------------

    crop_mrz_from_candidates(
        str(processed_path),
        mrz_candidates,
        str(mrz_path)
    )

    # --------------------------------------------------
    # 7. MRZ OCR
    # --------------------------------------------------

    mrz_ocr_results = run_ocr(
        str(mrz_path)
    )

    mrz_lines = find_mrz_candidates(
        mrz_ocr_results
    )

    mrz_lines.sort(
        key=lambda item: min(
            point[1]
            for point in item["box"]
        )
    )

    if len(mrz_lines) < 2:

        return {
            "status": "manual_review",
            "reason": (
                "MRZ was located but could not "
                "be read as two lines."
            ),
            "visual_fields": visual_fields,
            "mrz": None,
            "forensics": forensics
        }

    # --------------------------------------------------
    # 8. MRZ PARSING
    # --------------------------------------------------

    line1 = mrz_lines[0]["text"]
    line2 = mrz_lines[1]["text"]

    mrz_data = parse_td3(
        line1,
        line2
    )

    # --------------------------------------------------
    # 9. MRZ VALIDATION
    # --------------------------------------------------

    mrz_validation = validate_mrz(
        line1,
        line2
    )

    # --------------------------------------------------
    # 10. VISUAL ↔ MRZ
    # --------------------------------------------------

    consistency = compare_passport_fields(
        visual_fields,
        mrz_data
    )

    # --------------------------------------------------
    # 11. SUMMARY
    # --------------------------------------------------

    failed_mrz_checks = [
        field
        for field, check
        in mrz_validation["checks"].items()
        if not check["valid"]
    ]

    mismatches = [
        result["field"]
        for result in consistency
        if result["status"] == "MISMATCH"
    ]

    partial_matches = [
        result["field"]
        for result in consistency
        if result["status"] == "PARTIAL"
    ]

    if failed_mrz_checks or mismatches:

        status = "manual_review"

    else:

        status = "no_consistency_issue_detected"

    return {
        "status": status,

        "visual_fields": visual_fields,

        "mrz": {
            "line1": line1,
            "line2": line2,
            "parsed": mrz_data
        },

        "mrz_validation": {
            "line1_length":
                mrz_validation["line1_length"],

            "line2_length":
                mrz_validation["line2_length"],

            "checks":
                mrz_validation["checks"]
        },

        "consistency": consistency,

        "forensics": forensics,

        "summary": {
            "mrz_validation_failures":
                len(failed_mrz_checks),

            "field_mismatches":
                len(mismatches),

            "partial_matches":
                len(partial_matches),

            "failed_mrz_fields":
                failed_mrz_checks,

            "mismatched_fields":
                mismatches,

            "partial_fields":
                partial_matches
        }
    }