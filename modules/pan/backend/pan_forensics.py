import cv2
import os


# ==========================================
# CONTROLLED TEST THRESHOLDS
# ==========================================

GLOBAL_CHANGE_THRESHOLD = 0.03
REGION_CHANGE_THRESHOLD = 0.20


# ==========================================
# REFERENCE COMPARISON
# ==========================================

def compare_with_reference(image_path, reference_path):

    result = {
        "reference_available": False,
        "changed_pixels": 0,
        "change_percentage": 0.0,
        "reference_tamper_signal": False,
        "reference_status": "NOT_CHECKED"
    }

    if not os.path.exists(reference_path):

        result["reference_status"] = (
            "REFERENCE_NOT_AVAILABLE"
        )

        return result

    image = cv2.imread(image_path)
    reference = cv2.imread(reference_path)

    if image is None or reference is None:

        result["reference_status"] = (
            "REFERENCE_COMPARISON_FAILED"
        )

        return result

    if image.shape != reference.shape:

        result["reference_status"] = (
            "IMAGE_SIZE_MISMATCH"
        )

        return result

    result["reference_available"] = True

    difference = cv2.absdiff(
        reference,
        image
    )

    gray_difference = cv2.cvtColor(
        difference,
        cv2.COLOR_BGR2GRAY
    )

    _, threshold = cv2.threshold(
        gray_difference,
        30,
        255,
        cv2.THRESH_BINARY
    )

    changed_count = cv2.countNonZero(
        threshold
    )

    total_pixels = (
        threshold.shape[0]
        * threshold.shape[1]
    )

    change_percentage = (
        changed_count / total_pixels
    ) * 100

    result["changed_pixels"] = changed_count

    result["change_percentage"] = round(
        change_percentage,
        2
    )

    if change_percentage > GLOBAL_CHANGE_THRESHOLD:

        result["reference_tamper_signal"] = True

        result["reference_status"] = "REVIEW"

    else:

        result["reference_status"] = (
            "NO_SIGNIFICANT_CHANGE"
        )

    return result


# ==========================================
# SUSPICIOUS REGION ANALYSIS
# ==========================================

def analyze_suspicious_regions(
    image_path,
    reference_path
):

    result = {
        "regions": [],
        "suspicious_regions": []
    }

    if not os.path.exists(reference_path):

        return result

    image = cv2.imread(image_path)
    reference = cv2.imread(reference_path)

    if image is None or reference is None:

        return result

    if image.shape != reference.shape:

        return result

    height, width = image.shape[:2]

    regions = {

        "PAN Number": (0.20, 0.32),

        "Name": (0.34, 0.46),

        "Father Name": (0.46, 0.58),

        "Date of Birth": (0.58, 0.70),

        "QR / Code Area": (0.70, 1.00)
    }

    for region_name, values in regions.items():

        top_ratio = values[0]
        bottom_ratio = values[1]

        top = int(
            height * top_ratio
        )

        bottom = int(
            height * bottom_ratio
        )

        image_region = image[
            top:bottom,
            0:width
        ]

        reference_region = reference[
            top:bottom,
            0:width
        ]

        difference = cv2.absdiff(
            reference_region,
            image_region
        )

        gray_difference = cv2.cvtColor(
            difference,
            cv2.COLOR_BGR2GRAY
        )

        _, threshold = cv2.threshold(
            gray_difference,
            30,
            255,
            cv2.THRESH_BINARY
        )

        changed = cv2.countNonZero(
            threshold
        )

        total = (
            threshold.shape[0]
            * threshold.shape[1]
        )

        percentage = (
            changed / total
        ) * 100

        percentage = round(
            percentage,
            2
        )

        if percentage > REGION_CHANGE_THRESHOLD:

            status = "REVIEW"

        else:

            status = "NO_SIGNIFICANT_CHANGE"

        region_result = {

            "region": region_name,

            "change_percentage": percentage,

            "status": status
        }

        result["regions"].append(
            region_result
        )

        if percentage > REGION_CHANGE_THRESHOLD:

            result[
                "suspicious_regions"
            ].append(
                region_name
            )

    return result


# ==========================================
# MAIN PAN FORENSIC ANALYSIS
# ==========================================

def analyze_pan_image(
    image_path,
    reference_path=None
):

    result = {

        "image_readable": False,

        "resolution": None,

        "file_size_kb": None,

        "low_resolution": False,

        "small_file": False,

        "tamper_signal": False,

        "reference_comparison": None,

        "suspicious_regions": None,

        "status": "INCONCLUSIVE",

        "flags": []
    }

    # --------------------------------------
    # CHECK IMAGE
    # --------------------------------------

    if not os.path.exists(image_path):

        result["flags"].append(
            "PAN image file not found"
        )

        return result

    # --------------------------------------
    # FILE SIZE
    # --------------------------------------

    file_size = os.path.getsize(
        image_path
    )

    result["file_size_kb"] = round(
        file_size / 1024,
        2
    )

    # --------------------------------------
    # READ IMAGE
    # --------------------------------------

    image = cv2.imread(
        image_path
    )

    if image is None:

        result["flags"].append(
            "Unable to read PAN image"
        )

        return result

    result["image_readable"] = True

    # --------------------------------------
    # RESOLUTION
    # --------------------------------------

    height, width = image.shape[:2]

    result["resolution"] = (
        f"{width} x {height}"
    )

    if width < 500 or height < 300:

        result["low_resolution"] = True

        result["flags"].append(
            "Low image resolution"
        )

    # --------------------------------------
    # FILE SIZE CHECK
    # --------------------------------------

    if file_size < 10 * 1024:

        result["small_file"] = True

        result["flags"].append(
            "Unusually small image file"
        )

    # --------------------------------------
    # REFERENCE COMPARISON
    # --------------------------------------

    if reference_path:

        reference_result = (
            compare_with_reference(
                image_path,
                reference_path
            )
        )

        result[
            "reference_comparison"
        ] = reference_result

        if reference_result[
            "reference_tamper_signal"
        ]:

            result["tamper_signal"] = True

            result["flags"].append(
                "Difference from reference image "
                "requires review"
            )

        # ----------------------------------
        # REGION ANALYSIS
        # ----------------------------------

        region_result = (
            analyze_suspicious_regions(
                image_path,
                reference_path
            )
        )

        result[
            "suspicious_regions"
        ] = region_result

        if region_result[
            "suspicious_regions"
        ]:

            result["flags"].append(
                "Changes detected in: "
                + ", ".join(
                    region_result[
                        "suspicious_regions"
                    ]
                )
            )

    # --------------------------------------
    # FINAL FORENSIC STATUS
    # --------------------------------------

    if result["tamper_signal"]:

        result["status"] = "REVIEW"

    elif result["low_resolution"]:

        result["status"] = "INCONCLUSIVE"

    elif result["small_file"]:

        result["status"] = "REVIEW"

    else:

        result["status"] = (
            "NO_BASIC_FORENSIC_FLAGS"
        )

    return result


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    # Tampered PAN
    image_path = (
        "input/tampered_pan.png"
    )

    # Original clean PAN
    reference_path = (
        "input/dummy_pan.png"
    )

    result = analyze_pan_image(
        image_path,
        reference_path
    )

    print(
        "----- PAN FORENSIC ANALYSIS -----"
    )

    print(
        "Image Readable :",
        result["image_readable"]
    )

    print(
        "Resolution     :",
        result["resolution"]
    )

    print(
        "File Size (KB) :",
        result["file_size_kb"]
    )

    print(
        "Tamper Signal  :",
        result["tamper_signal"]
    )

    print(
        "Status         :",
        result["status"]
    )

    print(
        "\n----- REFERENCE COMPARISON -----"
    )

    reference = result[
        "reference_comparison"
    ]

    print(
        "Reference Available :",
        reference[
            "reference_available"
        ]
    )

    print(
        "Changed Pixels      :",
        reference[
            "changed_pixels"
        ]
    )

    print(
        "Change Percentage   :",
        reference[
            "change_percentage"
        ],
        "%"
    )

    print(
        "Reference Status    :",
        reference[
            "reference_status"
        ]
    )

    print(
        "\n----- SUSPICIOUS REGIONS -----"
    )

    for region in result[
        "suspicious_regions"
    ]["regions"]:

        print(
            region["region"],
            ":",
            region["change_percentage"],
            "%",
            "->",
            region["status"]
        )

    if result["flags"]:

        print(
            "\nForensic Flags:"
        )

        for flag in result["flags"]:

            print(
                "-",
                flag
            )

    else:

        print(
            "\nNo forensic issues detected."
        )