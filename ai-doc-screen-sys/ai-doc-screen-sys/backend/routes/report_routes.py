from flask import Blueprint, jsonify, request, send_file
from services.report_generator import build_report

report_bp = Blueprint("report", __name__)


@report_bp.route("/api/reports/generate", methods=["POST"])
def generate_report():
    data = request.get_json(silent=True) or {}
    try:
        pdf_stream = build_report(data)
        doc_id = data.get("document_id", "DAKSH-SCREENING")
        filename = f"daksh-report-{doc_id}.pdf"
        return send_file(
            pdf_stream,
            as_attachment=True,
            download_name=filename,
            mimetype="application/pdf"
        )
    except Exception as exc:
        return jsonify({"error": f"Failed to generate report: {str(exc)}"}), 500
