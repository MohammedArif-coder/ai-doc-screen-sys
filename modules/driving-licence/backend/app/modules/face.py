import cv2
from pathlib import Path



BACKEND_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BACKEND_DIR
    / "models"
    / "face_detection_yunet_2023mar.onnx"
)


def create_face_detector(width, height):
    return cv2.FaceDetectorYN.create(
        str(MODEL_PATH),
        "",
        (width, height),
        0.8,
        0.3,
        5000
    )


def detect_faces(image):
    height, width = image.shape[:2]

    detector = create_face_detector(
        width,
        height
    )

    _, faces = detector.detect(image)

    if faces is None:
        return []

    return faces


def build_face_box(face, width, height):
    x = int(face[0])
    y = int(face[1])
    w = int(face[2])
    h = int(face[3])

    x = max(0, x)
    y = max(0, y)

    w = min(w, width - x)
    h = min(h, height - y)

    return {
        "x": x,
        "y": y,
        "width": w,
        "height": h
    }


def calculate_face_area_ratio(
    face_box,
    image_width,
    image_height
):
    face_area = (
        face_box["width"]
        * face_box["height"]
    )

    document_area = (
        image_width * image_height
    )

    if document_area <= 0:
        return 0.0

    return face_area / document_area


def detect_face(image_path: str) -> dict:

    image = cv2.imread(image_path)

    # --------------------------------------------------
    # IMAGE READ CHECK
    # --------------------------------------------------

    if image is None:
        return {
            "face_detected": False,
            "face_count": 0,
            "status": "ERROR",
            "photo_consistency": "REVIEW",
            "verification_status": "UNABLE_TO_VERIFY",
            "message": "Unable to read document image."
        }

    # --------------------------------------------------
    # MODEL CHECK
    # --------------------------------------------------

    if not MODEL_PATH.exists():
        return {
            "face_detected": False,
            "face_count": 0,
            "status": "ERROR",
            "photo_consistency": "REVIEW",
            "verification_status": "UNABLE_TO_VERIFY",
            "message": (
                "YuNet face detection model is missing."
            )
        }

    # --------------------------------------------------
    # FACE DETECTION
    # --------------------------------------------------

    height, width = image.shape[:2]

    faces = detect_faces(image)

    face_count = len(faces)

    # --------------------------------------------------
    # NO FACE
    # --------------------------------------------------

    if face_count == 0:
        return {
            "face_detected": False,
            "face_count": 0,
            "status": "REVIEW",
            "photo_consistency": "REVIEW",
            "verification_status": "UNABLE_TO_VERIFY",
            "message": (
                "No face was detected in the document image. "
                "The photograph region could not be verified."
            )
        }

    # --------------------------------------------------
    # MULTIPLE FACES
    # --------------------------------------------------

    if face_count > 1:
        return {
            "face_detected": True,
            "face_count": face_count,
            "status": "REVIEW",
            "photo_consistency": "REVIEW",
            "verification_status": "MULTIPLE_FACES",
            "message": (
                "Multiple faces were detected in the document image. "
                "The photograph region cannot be reliably verified."
            )
        }

    # --------------------------------------------------
    # SINGLE FACE
    # --------------------------------------------------

    face = faces[0]

    face_box = build_face_box(
        face,
        width,
        height
    )

    face_ratio = calculate_face_area_ratio(
        face_box,
        width,
        height
    )

    # --------------------------------------------------
    # FACE TOO SMALL
    # --------------------------------------------------

    if face_ratio < 0.005:
        return {
            "face_detected": True,
            "face_count": 1,
            "status": "REVIEW",
            "photo_consistency": "REVIEW",
            "verification_status": "FACE_TOO_SMALL",
            "face_box": face_box,
            "face_area_ratio": round(
                face_ratio,
                4
            ),
            "message": (
                "One face was detected, but the face region "
                "is too small for reliable photograph analysis."
            )
        }

    # --------------------------------------------------
    # SINGLE FACE BUT NO REFERENCE IMAGE
    # --------------------------------------------------
    # Important:
    # Detecting one face does NOT prove that the face
    # belongs to the genuine licence holder.
    #
    # Without an authorised reference face, the system
    # should send this case for review instead of saying
    # that the photograph is verified.
    # --------------------------------------------------

    return {
        "face_detected": True,
        "face_count": 1,
        "status": "REVIEW",
        "photo_consistency": "REVIEW",
        "verification_status": "REFERENCE_FACE_REQUIRED",
        "face_box": face_box,
        "face_area_ratio": round(
            face_ratio,
            4
        ),
        "message": (
            "One suitable face was detected, but identity "
            "consistency cannot be verified without an "
            "authorized reference face."
        )
    }