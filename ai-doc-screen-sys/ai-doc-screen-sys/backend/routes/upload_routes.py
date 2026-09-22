import uuid
from pathlib import Path
from flask import Blueprint, jsonify, request, send_file
from werkzeug.utils import secure_filename

upload_bp = Blueprint("upload", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@upload_bp.route("/api/visa/upload", methods=["POST"])
def upload_visa():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "Please select a visa document image to upload."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file format. Please upload a PNG, JPG, or JPEG image."}), 415

    # Security check: Read file content length if possible
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    if size > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds limit (10MB maximum)."}), 400

    extension = file.filename.rsplit(".", 1)[1].lower()
    saved_filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = UPLOADS_DIR / saved_filename
    file.save(file_path)

    return jsonify({
        "upload_id": saved_filename,
        "filename": secure_filename(file.filename),
        "preview_url": f"/api/uploads/{saved_filename}",
        "size_bytes": size,
    })


@upload_bp.route("/api/uploads/<name>", methods=["GET"])
def get_uploaded_file(name):
    safe_name = secure_filename(name)
    file_path = UPLOADS_DIR / safe_name
    if not file_path.exists():
        return jsonify({"error": "Uploaded file not found."}), 404
    return send_file(file_path)
