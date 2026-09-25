from app.passport.ocr import run_ocr
from app.passport.field_extractor import extract_visual_fields
from app.passport.mrz_preprocess import crop_mrz
from app.passport.mrz import find_mrz_candidates
from app.passport.mrz_parser import parse_td3
from app.passport.mrz_validator import validate_mrz
from app.passport.consistency import compare_passport_fields


IMAGE_PATH = "app/passport/artifacts/processed.jpg"
MRZ_CROP_PATH = "app/passport/artifacts/mrz_crop.png"


print("\n" + "=" * 70)
print("PASSPORT SCREENING PIPELINE")
print("=" * 70)


# --------------------------------------------------
# 1. FULL-PAGE OCR
# --------------------------------------------------

print("\n[1] Running full-page OCR...")

ocr_results = run_ocr(IMAGE_PATH)

print(f"OCR detections: {len(ocr_results)}")


# --------------------------------------------------
# 2. VISUAL FIELD EXTRACTION
# --------------------------------------------------

print("\n[2] Extracting visual passport fields...")

visual_fields = extract_visual_fields(ocr_results)

print("\nVISUAL FIELDS")
print("-" * 50)

for key, value in visual_fields.items():
    print(f"{key}: {value}")


# --------------------------------------------------
# 3. MRZ CROP
# --------------------------------------------------

print("\n[3] Creating MRZ crop...")

crop_mrz(
    IMAGE_PATH,
    MRZ_CROP_PATH
)

print("MRZ crop created.")


# --------------------------------------------------
# 4. MRZ-ONLY OCR
# --------------------------------------------------

print("\n[4] Running MRZ-only OCR...")

mrz_ocr_results = run_ocr(MRZ_CROP_PATH)

mrz_candidates = find_mrz_candidates(mrz_ocr_results)

mrz_candidates.sort(
    key=lambda item: min(point[1] for point in item["box"])
)

print(f"MRZ candidates: {len(mrz_candidates)}")


if len(mrz_candidates) < 2:

    print("ERROR: Could not detect two MRZ lines.")

    exit()


line1 = mrz_candidates[0]["text"]
line2 = mrz_candidates[1]["text"]


print("\nMRZ LINE 1")
print(line1)

print("\nMRZ LINE 2")
print(line2)


# --------------------------------------------------
# 5. MRZ PARSING
# --------------------------------------------------

print("\n[5] Parsing MRZ...")

mrz_data = parse_td3(
    line1,
    line2
)

print("\nPARSED MRZ")
print("-" * 50)

for key, value in mrz_data.items():
    print(f"{key}: {value}")


# --------------------------------------------------
# 6. MRZ VALIDATION
# --------------------------------------------------

print("\n[6] Validating MRZ...")

mrz_validation = validate_mrz(
    line1,
    line2
)

print("\nMRZ CHECKS")
print("-" * 50)

for field, check in mrz_validation["checks"].items():

    status = "PASS" if check["valid"] else "FAIL"

    print(
        f"{field}: {status} "
        f"(expected={check['expected']}, "
        f"calculated={check['calculated']})"
    )


# --------------------------------------------------
# 7. VISUAL ↔ MRZ CONSISTENCY
# --------------------------------------------------

print("\n[7] Comparing visual fields with MRZ...")

consistency_results = compare_passport_fields(
    visual_fields,
    mrz_data
)

print("\nCONSISTENCY CHECK")
print("-" * 50)

for result in consistency_results:

    print(
        f"{result['field']}: "
        f"{result['status']}"
    )

    print(
        f"  Visual: {result['visual']}"
    )

    print(
        f"  MRZ:    {result['mrz']}"
    )


# --------------------------------------------------
# 8. REVIEW SUMMARY
# --------------------------------------------------

print("\n" + "=" * 70)
print("SCREENING SUMMARY")
print("=" * 70)


failed_mrz_checks = [
    field
    for field, check in mrz_validation["checks"].items()
    if not check["valid"]
]


mismatches = [
    result["field"]
    for result in consistency_results
    if result["status"] == "MISMATCH"
]


partial_matches = [
    result["field"]
    for result in consistency_results
    if result["status"] == "PARTIAL"
]


print(
    f"\nMRZ validation failures: "
    f"{len(failed_mrz_checks)}"
)

print(
    f"Field mismatches: "
    f"{len(mismatches)}"
)

print(
    f"Partial matches: "
    f"{len(partial_matches)}"
)


if failed_mrz_checks or mismatches:
    print("\nResult: MANUAL REVIEW REQUIRED")
else:
    print("\nResult: NO CONSISTENCY ISSUE DETECTED")


print("\nPipeline completed.")