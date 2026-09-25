import cv2
from PIL import Image, ImageOps


def load_image(image_path):
    try:
        pil_image = Image.open(image_path)

        # Correct camera/EXIF orientation
        pil_image = ImageOps.exif_transpose(pil_image)

        # Convert to RGB
        pil_image = pil_image.convert("RGB")

        # Convert PIL RGB -> OpenCV BGR
        image = cv2.cvtColor(
            __import__("numpy").array(pil_image),
            cv2.COLOR_RGB2BGR
        )

        return image

    except Exception as e:
        raise ValueError(f"Unable to read image: {e}")


def resize_image(image, max_dimension=2000):
    height, width = image.shape[:2]

    largest_dimension = max(height, width)

    if largest_dimension <= max_dimension:
        return image, False

    scale = max_dimension / largest_dimension

    new_width = int(width * scale)
    new_height = int(height * scale)

    resized = cv2.resize(
        image,
        (new_width, new_height),
        interpolation=cv2.INTER_AREA
    )

    return resized, True


def create_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def enhance_contrast(gray_image):
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    return clahe.apply(gray_image)


def preprocess_image(image_path):
    original = load_image(image_path)

    processed, resized = resize_image(original)

    gray = create_grayscale(processed)

    enhanced = enhance_contrast(gray)

    return {
        "original": original,
        "processed": processed,
        "gray": gray,
        "enhanced": enhanced,
        "was_resized": resized
    }