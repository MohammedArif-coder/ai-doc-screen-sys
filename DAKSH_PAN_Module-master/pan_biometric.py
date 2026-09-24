from PIL import Image
import os


def analyze_photo_region(image_path):
    result = {
        "photo_region_detected": False,
        "photo_region_size": None,
        "status": "INCONCLUSIVE",
        "flags": []
    }

    if not os.path.exists(image_path):
        result["flags"].append("PAN image file not found")
        return result

    try:
        image = Image.open(image_path)
        width, height = image.size

        # Approximate photo region for our sample PAN layout.
        # This is a prototype and can be adjusted for different layouts.
        photo_left = int(width * 0.68)
        photo_top = int(height * 0.20)
        photo_right = int(width * 0.95)
        photo_bottom = int(height * 0.80)

        photo_width = photo_right - photo_left
        photo_height = photo_bottom - photo_top

        result["photo_region_size"] = (
            f"{photo_width} x {photo_height}"
        )

        # Check whether the estimated region has usable dimensions
        if photo_width > 50 and photo_height > 50:
            result["photo_region_detected"] = True
            result["status"] = "PHOTO_REGION_AVAILABLE"
        else:
            result["flags"].append(
                "Photo region is too small for analysis"
            )
            result["status"] = "REVIEW"

    except Exception as error:
        result["flags"].append(
            f"Unable to analyze photo region: {error}"
        )

    return result


if __name__ == "__main__":

    image_path = "input/dummy_pan.png"

    result = analyze_photo_region(image_path)

    print("----- PAN BIOMETRIC ANALYSIS -----")

    print(
        "Photo Region Detected :",
        result["photo_region_detected"]
    )

    print(
        "Photo Region Size     :",
        result["photo_region_size"]
    )

    print(
        "Status                :",
        result["status"]
    )

    if result["flags"]:
        print("\nBiometric Flags:")

        for flag in result["flags"]:
            print("-", flag)

    else:
        print("\nNo basic photo-region issues detected.")