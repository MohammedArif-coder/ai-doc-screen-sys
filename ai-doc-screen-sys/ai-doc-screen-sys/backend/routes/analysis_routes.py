import json
from pathlib import Path
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from database import save_screening, list_screenings
from services.ocr_service import extract_text
from services.image_analysis import analyze_image
from services.tamper_detection import detect_tamper
from services.consistency_checker import check_consistency
from services.risk_engine import calculate_risk

analysis_bp = Blueprint("analysis", __name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOADS_DIR = BASE_DIR / "uploads"
DEMO_DIR = BASE_DIR / "demo_data" / "demo_visas"
META_DIR = BASE_DIR / "demo_data" / "metadata"


def read_metadata(document_id):
    if not document_id:
        return {}
    path = META_DIR / f"{secure_filename(document_id)}.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def run_full_analysis(file_path, document_id=None, fallback_text=""):
    metadata = read_metadata(document_id) if document_id else {}

    if not fallback_text and metadata:
        expiry = "[ ALTERED / EXPIRATION MISMATCH ]" if metadata.get("anomaly") == "date_mismatch" else "14/01/2029"
        visa_no = "[ ALTERED / INVALID VISA NO ]" if metadata.get("anomaly") == "altered_region" else "V987654321"
        applicant = metadata.get("applicant", "JOHN DOE")
        passport_no = metadata.get("passport_no", "A12345678")
        visa_type = metadata.get("visa_type", "TOURIST")

        fallback_text = "\n".join([
            "OFFICIAL ENTRY VISA / VISA D'ENTREE",
            f"FULL NAME: {applicant}",
            f"PASSPORT NO: {passport_no}",
            f"VISA NUMBER: {visa_no}",
            f"VISA TYPE: {visa_type}",
            "ISSUE DATE: 15/01/2024",
            f"EXPIRY DATE: {expiry}",
            "NATIONALITY: INDIAN",
            "DEMO - NOT A REAL VISA",
        ])

    ocr_result = extract_text(file_path, fallback_text=fallback_text)
    image_result = analyze_image(file_path, quality_hint=metadata.get("quality_hint"))
    consistency_result = check_consistency(ocr_result["fields"], metadata)
    tamper_result = detect_tamper(file_path, metadata=metadata, image_stats=image_result)
    risk_result = calculate_risk(ocr_result, image_result, consistency_result, tamper_result)

    findings = consistency_result["findings"][:]

    if tamper_result["signal_detected"] or tamper_result["category"] == "SUSPICIOUS SIGNAL":
        if not any(f.get("type") == "image_anomaly" for f in findings):
            findings.append({
                "type": "image_anomaly",
                "severity": "high",
                "message": "Potential image manipulation / altered text region detected.",
                "location": "Highlighted document region"
            })

    if not findings:
        findings.append({
            "type": "required_fields",
            "severity": "low",
            "message": "All document fields verified. No tampering signals detected.",
            "location": "Document Canvas"
        })

    doc_id_val = document_id or ocr_result["fields"].get("passport_no") or "DMS-UPLOADED"
    doc_name = file_path.name

    result = {
        "document_id": doc_id_val,
        "document_name": doc_name,
        "document_type": "Official Entry Visa",
        "verdict": risk_result["verdict"],
        "authenticity_score": risk_result["authenticity_score"],
        "status": risk_result["status"],
        "scores": {
            "authenticity": risk_result["authenticity_score"],
            "ocr": ocr_result["confidence"],
            "consistency": consistency_result["score"],
            "image_quality": image_result["score"]
        },
        "findings": findings,
        "tamper_analysis": tamper_result,
        "ocr": ocr_result,
        "image_analysis": image_result,
        "consistency": consistency_result,
        "reason": risk_result["reason"],
        "recommendation": "Manual verification recommended for flagged anomalies."
    }

    try:
        save_screening(result, doc_name)
    except Exception as err:
        print(f"Database save warning: {err}")

    return result


@analysis_bp.route("/api/visa/analyze", methods=["POST"])
def analyze_document():
    data = request.get_json(silent=True) or {}
    upload_id = data.get("upload_id")
    document_id = data.get("document_id")

    if document_id:
        file_path = DEMO_DIR / f"{secure_filename(document_id)}.png"
        if not file_path.exists():
            return jsonify({"error": f"Demo document '{document_id}' not found."}), 404
    elif upload_id:
        file_path = UPLOADS_DIR / secure_filename(upload_id)
        if not file_path.exists():
            return jsonify({"error": "Uploaded document file not found."}), 404
    else:
        return jsonify({"error": "No document specified for analysis. Provide 'upload_id' or 'document_id'."}), 400

    analysis_output = run_full_analysis(
        file_path,
        document_id=document_id,
        fallback_text=data.get("fallback_text", "")
    )
    return jsonify(analysis_output)


@analysis_bp.route("/api/visa/history", methods=["GET"])
def get_history():
    return jsonify(list_screenings())
