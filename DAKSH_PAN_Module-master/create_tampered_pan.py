import cv2
import os


def create_tampered_pan():

    original_path = "input/dummy_pan.png"
    tampered_path = "input/tampered_pan.png"

    # ---------------------------------------
    # CHECK ORIGINAL IMAGE
    # ---------------------------------------

    if not os.path.exists(original_path):

        print("Original PAN image not found.")
        return

    image = cv2.imread(original_path)

    if image is None:

        print("Unable to read original PAN image.")
        return

    # Make a copy so the original is never changed
    tampered = image.copy()

    height, width = tampered.shape[:2]

    # ---------------------------------------
    # 1. SMALL ALTERATION IN FATHER'S NAME
    # ---------------------------------------

    # Approximate Father's Name area
    # We modify only a small portion.

    x1 = int(width * 0.18)
    y1 = int(height * 0.50)

    x2 = int(width * 0.31)
    y2 = int(height * 0.54)

    # Create a soft/light alteration instead
    # of a large white rectangle.

    original_region = tampered[
        y1:y2,
        x1:x2
    ]

    altered_region = cv2.GaussianBlur(
        original_region,
        (9, 9),
        0
    )

    # Blend the altered region slightly
    tampered[
        y1:y2,
        x1:x2
    ] = cv2.addWeighted(
        original_region,
        0.35,
        altered_region,
        0.65,
        0
    )

    # ---------------------------------------
    # 2. SMALL QR / CODE ALTERATION
    # ---------------------------------------

    # Approximate QR area based on the
    # synthetic PAN layout.

    qr_x1 = int(width * 0.69)
    qr_y1 = int(height * 0.28)

    qr_x2 = int(width * 0.76)
    qr_y2 = int(height * 0.35)

    qr_region = tampered[
        qr_y1:qr_y2,
        qr_x1:qr_x2
    ]

    # Slightly blur a small part of the QR area.
    # This simulates a controlled alteration.

    qr_blurred = cv2.GaussianBlur(
        qr_region,
        (5, 5),
        0
    )

    tampered[
        qr_y1:qr_y2,
        qr_x1:qr_x2
    ] = cv2.addWeighted(
        qr_region,
        0.40,
        qr_blurred,
        0.60,
        0
    )

    # ---------------------------------------
    # SAVE TAMPERED IMAGE
    # ---------------------------------------

    cv2.imwrite(
        tampered_path,
        tampered
    )

    print("--------------------------------------")
    print("Tampered PAN created successfully.")
    print("Original :", original_path)
    print("Tampered :", tampered_path)
    print("--------------------------------------")


if __name__ == "__main__":

    create_tampered_pan()