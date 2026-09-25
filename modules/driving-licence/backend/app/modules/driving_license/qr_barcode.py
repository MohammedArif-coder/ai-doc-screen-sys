import cv2


def detect_qr_barcode(image_path: str) -> dict:
    """
    Detect QR codes and barcodes from a Driving Licence image.
    """

    image = cv2.imread(image_path)

    if image is None:
        return {
            "detected": False,
            "type": None,
            "data": None,
            "message": "Unable to read document image."
        }

    # Create OpenCV QR detector
    qr_detector = cv2.QRCodeDetector()

    # Try to detect QR code
    data, points, _ = qr_detector.detectAndDecode(image)

    if points is not None and data:
        return {
            "detected": True,
            "type": "QR",
            "data": data,
            "message": "QR code detected successfully."
        }

    # Try barcode detection if available
    try:
        barcode_detector = cv2.barcode.BarcodeDetector()

        barcode_data, barcode_type, _ = barcode_detector.detectAndDecode(
            image
        )

        if barcode_data:
            return {
                "detected": True,
                "type": "BARCODE",
                "data": barcode_data,
                "message": "Barcode detected successfully."
            }

    except AttributeError:
        pass

    return {
        "detected": False,
        "type": None,
        "data": None,
        "message": "No QR code or barcode detected."
    }