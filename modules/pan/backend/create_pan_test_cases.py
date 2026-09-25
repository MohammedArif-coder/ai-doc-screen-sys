import cv2
import os


INPUT_FOLDER = "input"
ORIGINAL_FILE = "input/dummy_pan.png"


def load_original():

    if not os.path.exists(ORIGINAL_FILE):
        print("dummy_pan.png not found.")
        return None

    image = cv2.imread(ORIGINAL_FILE)

    if image is None:
        print("Unable to read dummy_pan.png.")
        return None

    print("Original PAN loaded successfully.")
    print("Image size:", image.shape[1], "x", image.shape[0])

    return image


def replace_field(
    original,
    x1,
    y1,
    x2,
    y2,
    new_text,
    output_name
):

    image = original.copy()

    # Cover only the existing value
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (255, 255, 255),
        -1
    )

    # Use the same type of font as the original synthetic PAN
    cv2.putText(
        image,
        new_text,
        (x1, y2 - 2),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.38,
        (0, 0, 0),
        1,
        cv2.LINE_AA
    )

    output_path = os.path.join(
        INPUT_FOLDER,
        output_name
    )

    cv2.imwrite(output_path, image)

    print("Created:", output_path)


# --------------------------------------------------
# TEST 2 - TAMPERED NAME
# --------------------------------------------------

def create_tampered_name(original):

    replace_field(
        original,
        102,
        210,
        180,
        219,
        "ARUN KUMAR",
        "pan_tampered_name.png"
    )


# --------------------------------------------------
# TEST 3 - TAMPERED FATHER NAME
# --------------------------------------------------

def create_tampered_father(original):

    replace_field(
        original,
        161,
        246,
        259,
        255,
        "RAJESH KUMAR",
        "pan_tampered_father.png"
    )


# --------------------------------------------------
# TEST 4 - TAMPERED DOB
# --------------------------------------------------

def create_tampered_dob(original):

    replace_field(
        original,
        155,
        280,
        225,
        293,
        "20/09/2004",
        "pan_tampered_dob.png"
    )


# --------------------------------------------------
# TEST 5 - TAMPERED PAN NUMBER
# --------------------------------------------------

def create_tampered_pan_number(original):

    replace_field(
        original,
        147,
        175,
        224,
        184,
        "ABCDE9876Z",
        "pan_tampered_number.png"
    )


# --------------------------------------------------
# TEST 6 - TAMPERED PHOTO
# --------------------------------------------------

def create_tampered_photo(original):

    image = original.copy()

    # Actual photo area from the uploaded synthetic PAN
    x1 = 637
    y1 = 145
    x2 = 779
    y2 = 293

    # Cover original synthetic photo
    cv2.rectangle(
        image,
        (x1, y1),
        (x2, y2),
        (210, 210, 210),
        -1
    )

    # Different synthetic test pattern
    cv2.rectangle(
        image,
        (x1 + 15, y1 + 15),
        (x2 - 15, y2 - 15),
        (160, 160, 160),
        -1
    )

    cv2.circle(
        image,
        (
            (x1 + x2) // 2,
            (y1 + y2) // 2
        ),
        35,
        (100, 100, 100),
        -1
    )

    cv2.putText(
        image,
        "TEST",
        (x1 + 35, y2 - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 0),
        2,
        cv2.LINE_AA
    )

    output_path = os.path.join(
        INPUT_FOLDER,
        "pan_tampered_photo.png"
    )

    cv2.imwrite(output_path, image)

    print("Created:", output_path)


# --------------------------------------------------
# TEST 7 - BLURRY PAN
# --------------------------------------------------

def create_blurry_pan(original):

    image = cv2.GaussianBlur(
        original,
        (21, 21),
        0
    )

    output_path = os.path.join(
        INPUT_FOLDER,
        "pan_blurry.png"
    )

    cv2.imwrite(output_path, image)

    print("Created:", output_path)


# --------------------------------------------------
# TEST 8 - MISSING NAME
# --------------------------------------------------

def create_missing_name(original):

    image = original.copy()

    # Remove only RAVI KUMAR.
    # NAME: label remains untouched.
    cv2.rectangle(
        image,
        (102, 210),
        (180, 219),
        (255, 255, 255),
        -1
    )

    output_path = os.path.join(
        INPUT_FOLDER,
        "pan_missing_field.png"
    )

    cv2.imwrite(output_path, image)

    print("Created:", output_path)


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print()
    print("======================================")
    print(" DAKSH - PAN TEST CASE GENERATOR")
    print("======================================")
    print()

    original = load_original()

    if original is None:
        return

    print()
    print("Creating synthetic PAN test cases...")
    print()

    create_tampered_name(original)

    create_tampered_father(original)

    create_tampered_dob(original)

    create_tampered_pan_number(original)

    create_tampered_photo(original)

    create_blurry_pan(original)

    create_missing_name(original)

    print()
    print("======================================")
    print(" ALL TEST CASES CREATED")
    print("======================================")
    print()


if __name__ == "__main__":
    main()