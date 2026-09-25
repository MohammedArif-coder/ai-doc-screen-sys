import cv2


def crop_mrz(image_path, output_path):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f"Could not read image: {image_path}")

    # MRZ region
    x1 = 300
    y1 = 1340
    x2 = 1110
    y2 = 1455

    mrz = image[y1:y2, x1:x2]

    # Enlarge
    mrz = cv2.resize(
        mrz,
        None,
        fx=4,
        fy=4,
        interpolation=cv2.INTER_CUBIC
    )

    # Grayscale
    gray = cv2.cvtColor(mrz, cv2.COLOR_BGR2GRAY)

    # Slight noise reduction
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    cv2.imwrite(output_path, gray)

    return output_path