from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


def build_report(result):
    """
    Generates a PDF document report containing document metadata, risk score breakdown,
    detected findings, tamper signals, and compulsory safety disclaimers.
    """
    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=letter)
    pdf.setTitle("DAKSH Visa Screening Report")

    # Dimensions
    page_width, page_height = letter

    # Header Banner
    pdf.setFillColor(colors.HexColor("#0f2738"))
    pdf.rect(0, page_height - 90, page_width, 90, fill=True, stroke=False)

    pdf.setFillColor(colors.HexColor("#5caecb"))
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(54, page_height - 45, "DAKSH | Document Screening Hub")

    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(colors.HexColor("#e9b765"))
    pdf.drawString(54, page_height - 68, "PROTOTYPE REPORT — FOR DEMONSTRATION / SCREENING TESTING ONLY")

    y = page_height - 120

    # Section 1: Overview Metadata
    pdf.setFillColor(colors.HexColor("#18303b"))
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(54, y, "Document Screening Summary")
    y -= 22

    pdf.setFont("Helvetica", 11)
    pdf.setFillColor(colors.black)

    doc_id = result.get("document_id", "DEMO-000123")
    doc_type = result.get("document_type", "Synthetic Visitor Permit")
    status_str = result.get("status", "review").replace("_", " ").upper()
    date_str = datetime.now().strftime("%d %B %Y, %H:%M UTC")

    meta_items = [
        ("Document ID:", doc_id),
        ("Document Type:", doc_type),
        ("Screening Date:", date_str),
        ("Screening Status:", status_str),
        ("OCR Quality Score:", f"{result.get('scores', {}).get('ocr', 0)}%"),
        ("Consistency Score:", f"{result.get('scores', {}).get('consistency', 0)}%"),
        ("Image Quality Score:", f"{result.get('scores', {}).get('image_quality', 0)}%"),
    ]

    for label, val in meta_items:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(54, y, label)
        pdf.setFont("Helvetica", 10)
        pdf.drawString(180, y, str(val))
        y -= 18

    y -= 10
    pdf.setStrokeColor(colors.HexColor("#cccccc"))
    pdf.setLineWidth(1)
    pdf.line(54, y, page_width - 54, y)
    y -= 25

    # Section 2: Detected Screening Signals & Findings
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.HexColor("#18303b"))
    pdf.drawString(54, y, "Detected Signals & Analysis Findings")
    y -= 22

    findings = result.get("findings", [])
    if not findings:
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawString(54, y, "No adverse screening signals recorded for this synthetic document.")
        y -= 20
    else:
        for item in findings:
            severity = item.get("severity", "medium").upper()
            msg = item.get("message", "Signal detected")
            loc = item.get("location", "Document")

            if severity == "HIGH":
                pdf.setFillColor(colors.HexColor("#a03b32"))
            elif severity == "MEDIUM":
                pdf.setFillColor(colors.HexColor("#c87a28"))
            else:
                pdf.setFillColor(colors.HexColor("#2d7d56"))

            pdf.setFont("Helvetica-Bold", 10)
            pdf.drawString(54, y, f"[{severity}]")

            pdf.setFillColor(colors.black)
            pdf.setFont("Helvetica", 10)
            pdf.drawString(110, y, f"{msg} ({loc})")
            y -= 20

    y -= 10
    pdf.line(54, y, page_width - 54, y)
    y -= 25

    # Section 3: Extracted Fictional Fields
    pdf.setFont("Helvetica-Bold", 14)
    pdf.setFillColor(colors.HexColor("#18303b"))
    pdf.drawString(54, y, "Extracted Document Fields (OCR)")
    y -= 22

    ocr_fields = result.get("ocr", {}).get("fields", {})
    if not ocr_fields:
        pdf.setFont("Helvetica-Oblique", 10)
        pdf.drawString(54, y, "No structured text fields extracted.")
        y -= 20
    else:
        for k, v in ocr_fields.items():
            field_name = k.replace("_", " ").title()
            field_val = v or "Not readable"
            pdf.setFont("Helvetica-Bold", 9)
            pdf.drawString(54, y, f"{field_name}:")
            pdf.setFont("Helvetica", 9)
            pdf.drawString(180, y, field_val)
            y -= 16

    y -= 15

    # Section 4: Mandatory Legal / Prototype Disclaimer Box
    pdf.setFillColor(colors.HexColor("#f4f7f8"))
    pdf.setStrokeColor(colors.HexColor("#2a526b"))
    pdf.rect(54, y - 60, page_width - 108, 60, fill=True, stroke=True)

    pdf.setFillColor(colors.HexColor("#18303b"))
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(64, y - 18, "RECOMMENDATION & MANDATORY NOTICE")

    pdf.setFont("Helvetica", 9)
    pdf.setFillColor(colors.HexColor("#445566"))
    pdf.drawString(64, y - 34, "Manual document verification is recommended before taking official decisions.")
    pdf.drawString(64, y - 48, "This system provides automated screening signals and is NOT a substitute for human review.")

    # Footer
    pdf.setFont("Helvetica", 8)
    pdf.setFillColor(colors.HexColor("#888888"))
    pdf.drawString(54, 30, "DAKSH v1.0 • Fictional Demonstration System • NOT A REAL VISA")

    pdf.save()
    output.seek(0)
    return output
