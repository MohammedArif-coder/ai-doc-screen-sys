import json
from pathlib import Path
from flask import Blueprint, jsonify, send_file
from werkzeug.utils import secure_filename

demo_bp = Blueprint("demo", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = BASE_DIR / "demo_data" / "demo_visas"
META_DIR = BASE_DIR / "demo_data" / "metadata"


def read_metadata(document_id):
    path = META_DIR / f"{secure_filename(document_id)}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


@demo_bp.route("/api/demo/documents", methods=["GET"])
def get_demo_documents():
    documents = []
    if META_DIR.exists():
        for path in sorted(META_DIR.glob("DEMO-*.json")):
            try:
                metadata = json.loads(path.read_text(encoding="utf-8"))
                documents.append({
                    **metadata,
                    "preview_url": f"/api/demo/documents/{metadata['id']}/image"
                })
            except Exception:
                continue
    return jsonify(documents)


@demo_bp.route("/api/demo/documents/<document_id>", methods=["GET"])
def get_demo_document_detail(document_id):
    metadata = read_metadata(document_id)
    if not metadata:
        return jsonify({"error": "Demo document metadata not found"}), 404
    return jsonify({
        **metadata,
        "preview_url": f"/api/demo/documents/{document_id}/image"
    })


@demo_bp.route("/api/demo/documents/<document_id>/image", methods=["GET"])
def get_demo_document_image(document_id):
    safe_id = secure_filename(document_id)
    file_path = DEMO_DIR / f"{safe_id}.png"
    if not file_path.exists():
        return jsonify({"error": "Demo image not found"}), 404
    return send_file(file_path, mimetype="image/png")
