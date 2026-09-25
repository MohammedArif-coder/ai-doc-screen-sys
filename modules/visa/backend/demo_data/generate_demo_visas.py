import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "demo_visas"
META = ROOT / "metadata"

FONT_PATH = "C:/Windows/Fonts/arial.ttf"
FONT_BOLD_PATH = "C:/Windows/Fonts/arialbd.ttf"
FONT_MONO_PATH = "C:/Windows/Fonts/cour.ttf"


def get_font(size, bold=False, mono=False):
    if mono and os.path.exists(FONT_MONO_PATH):
        return ImageFont.truetype(FONT_MONO_PATH, size)
    target = FONT_BOLD_PATH if bold else FONT_PATH
    if os.path.exists(target):
        return ImageFont.truetype(target, size)
    elif os.path.exists(FONT_PATH):
        return ImageFont.truetype(FONT_PATH, size)
    return ImageFont.load_default()


# EXACT 3 MODEL VISAS
CASES = [
    ("DEMO-01", "JOHN DOE", "original", "ORIGINAL / AUTHENTIC VISA", 100),
    ("DEMO-02", "JANE DOE", "tampered", "TAMPERED VISA (Altered Expiry & Visa No)", 35),
    ("DEMO-03", "FAKE APPLICANT", "fully_faked", "FULLY FAKED VISA (Counterfeit MRZ & Invalid Data)", 10),
]


def draw_avatar(draw, x0, y0, x1, y1, is_fake=False):
    """Draws avatar character."""
    bg_color = "#fecaca" if is_fake else "#dbe5f0"
    draw.rectangle((x0, y0, x1, y1), fill=bg_color, outline="#dc2626" if is_fake else "#2b4c7e", width=2)

    # Shirt
    draw.polygon([(x0 + 20, y1), (x0 + (x1 - x0) // 2, y0 + 130), (x1 - 20, y1)], fill="#7f1d1d" if is_fake else "#1e3f76")

    # Neck
    draw.rectangle((x0 + 75, y0 + 120, x0 + 105, y0 + 145), fill="#e0b094")

    # Head
    draw.ellipse((x0 + 40, y0 + 60, x0 + 140, y0 + 150), fill="#e0b094")

    # Hair
    draw.chord((x0 + 38, y0 + 35, x0 + 142, y0 + 100), 180, 360, fill="#3b2c20")

    # Eyes & Mouth lines
    draw.rectangle((x0 + 63, y0 + 95, x0 + 78, y0 + 101), fill="#3b2c20")
    draw.rectangle((x0 + 102, y0 + 95, x0 + 117, y0 + 101), fill="#3b2c20")
    draw.line((x0 + 90, y0 + 105, x0 + 90, y0 + 120), fill="#b5886d", width=2)
    draw.line((x0 + 75, y0 + 132, x0 + 105, y0 + 132), fill="#b95858", width=2)

    if is_fake:
        draw.text((x0 + 35, y0 + 175), "FAKE PHOTO", fill="#dc2626", font=get_font(12, bold=True))


def draw_official_seal(draw, cx, cy, radius, is_fake=False):
    color = "#f87171" if is_fake else "#cbd5e1"
    text_color = "#dc2626" if is_fake else "#94a3b8"
    draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=color, width=3)
    draw.text((cx - 28, cy - 12), "COUNTERFEIT" if is_fake else "OFFICIAL", fill=text_color, font=get_font(10, bold=is_fake))
    draw.text((cx - 18, cy + 4), "SEAL" if is_fake else "SEAL", fill=text_color, font=get_font(10, bold=is_fake))


def make_case(case_id, applicant, anomaly, description, quality):
    width, height = 1000, 570
    bg_color = "#ffffff"
    image = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Background pinstripes
    stripe_color = "#fef2f2" if anomaly == "fully_faked" else "#f1f5f9"
    for y in range(85, 420, 12):
        draw.line((24, y, width - 24, y), fill=stripe_color, width=1)

    # Outer border
    border_color = "#dc2626" if anomaly == "fully_faked" else "#1e3f76"
    draw.rectangle((18, 18, width - 18, height - 18), outline=border_color, width=4)

    # Header Bar
    header_color = "#991b1b" if anomaly == "fully_faked" else "#1e3f76"
    draw.rectangle((22, 22, width - 22, 85), fill=header_color)

    header_title = "COUNTERFEIT ENTRY VISA / FAKE PERMIT" if anomaly == "fully_faked" else "OFFICIAL ENTRY VISA / VISA D'ENTREE"
    draw.text((width // 2 - (150 if anomaly == "fully_faked" else 130), 42), header_title, fill="#ffffff", font=get_font(14, bold=True))

    # Avatar on left
    draw_avatar(draw, 50, 115, 230, 320, is_fake=(anomaly == "fully_faked"))

    # Official seal on right
    draw_official_seal(draw, 880, 180, 60, is_fake=(anomaly == "fully_faked"))

    # Fields setup
    start_x = 260

    if anomaly == "original":
        passport_no = "A12345678"
        visa_no = "V987654321"
        visa_type = "TOURIST"
        issue_date = "15/01/2024"
        expiry_date = "14/01/2029"
        nationality = "INDIAN"
    elif anomaly == "tampered":
        passport_no = "A12345678"
        visa_no = "V987654321"
        visa_type = "BUSINESS"
        issue_date = "15/01/2025"
        expiry_date = "14/01/2030"
        nationality = "INDIAN"
    else:  # fully_faked
        passport_no = "INVALID999"
        visa_no = "V000000000"
        visa_type = "UNVERIFIED"
        issue_date = "01/01/2026"
        expiry_date = "01/01/2020"  # Expired / Fake date
        nationality = "UNKNOWN"

    fields = [
        ("FULL NAME:", applicant),
        ("PASSPORT NO:", passport_no),
        ("VISA NUMBER:", visa_no),
        ("VISA TYPE:", visa_type),
        ("ISSUE DATE:", issue_date),
        ("EXPIRY DATE:", expiry_date),
        ("NATIONALITY:", nationality),
    ]

    for index, (label, val) in enumerate(fields):
        y = 115 + index * 30
        draw.text((start_x, y), label, fill="#475569", font=get_font(12, bold=True))

        if anomaly == "tampered" and label == "EXPIRY DATE:":
            draw.rectangle((start_x + 180, y - 4, start_x + 440, y + 22), fill="#fde8e8", outline="#b92c2c", width=2)
            draw.text((start_x + 190, y), "[ ALTERED / EXPIRATION MISMATCH ]", fill="#b92c2c", font=get_font(11, bold=True))
        elif anomaly == "fully_faked" and label in ["PASSPORT NO:", "VISA NUMBER:", "EXPIRY DATE:"]:
            draw.rectangle((start_x + 180, y - 4, start_x + 440, y + 22), fill="#fecaca", outline="#dc2626", width=2)
            draw.text((start_x + 190, y), f"[ FAKE / {val} ]", fill="#991b1b", font=get_font(11, bold=True))
        else:
            draw.text((start_x + 180, y), val, fill="#0f172a", font=get_font(12, bold=True))

    # Bottom Machine Readable Zone (MRZ Box)
    mrz_x0, mrz_y0, mrz_x1, mrz_y1 = 40, 430, 960, 535
    mrz_bg = "#fecaca" if anomaly == "fully_faked" else "#eef3f8"
    mrz_border = "#dc2626" if anomaly == "fully_faked" else "#cbd5e1"
    draw.rectangle((mrz_x0, mrz_y0, mrz_x1, mrz_y1), fill=mrz_bg, outline=mrz_border, width=2)

    if anomaly == "original":
        mrz_line1 = "V<INDDOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        mrz_line2 = "A123456783IND9001015M2901148<<<<<<<<<<<<<<<"
    elif anomaly == "tampered":
        mrz_line1 = "V<INDDOE<<JANE<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        mrz_line2 = "A123456783IND9001015M3001148<<<<<<<<<<<<<<<"
    else:  # fully_faked
        mrz_line1 = "V<XXXFAKE<<COUNTERFEIT<<<<<<<<<<<<<<<<<<<<<"
        mrz_line2 = "INVALID999XXX0000000F0000000<<<<<<<<<<<<<<<"

    draw.text((mrz_x0 + 20, mrz_y0 + 18), mrz_line1, fill="#991b1b" if anomaly == "fully_faked" else "#1e293b", font=get_font(13, bold=True, mono=True))
    draw.text((mrz_x0 + 20, mrz_y0 + 54), mrz_line2, fill="#991b1b" if anomaly == "fully_faked" else "#1e293b", font=get_font(13, bold=True, mono=True))

    # Watermark Banner
    draw.rectangle((mrz_x1 - 280, mrz_y0 + 12, mrz_x1 - 15, mrz_y0 + 40), fill="#fecaca", outline="#dc2626", width=1)
    draw.text((mrz_x1 - 270, mrz_y0 + 18), "DEMO – NOT A REAL VISA", fill="#991b1b", font=get_font(11, bold=True))

    # Save PNG image
    path = OUT / f"{case_id}.png"
    image.save(path)

    # Save JSON metadata for the 3 cases
    metadata = {
        "id": case_id,
        "applicant": applicant,
        "passport_no": passport_no,
        "visa_no": visa_no,
        "visa_type": visa_type,
        "anomaly": anomaly,
        "description": description,
        "quality_hint": quality,
        "expected_findings": []
    }

    if anomaly == "tampered":
        metadata["expected_findings"].append({
            "type": "date_inconsistency",
            "severity": "high",
            "message": "Expiration date contains an altered mismatch tag.",
            "location": "EXPIRY DATE field"
        })
    elif anomaly == "fully_faked":
        metadata["expected_findings"].append({
            "type": "counterfeit_mrz",
            "severity": "high",
            "message": "MRZ checksum validation failed; invalid passport number (INVALID999).",
            "location": "MRZ Zone & Passport Field"
        })
        metadata["expected_findings"].append({
            "type": "invalid_seal",
            "severity": "high",
            "message": "Official seal pattern fail; counterfeit stamp detected.",
            "location": "Official Seal area"
        })

    (META / f"{case_id}.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)

    # Clean existing meta & images
    for f in OUT.glob("DEMO-*.png"):
        f.unlink()
    for f in META.glob("DEMO-*.json"):
        f.unlink()

    for case in CASES:
        make_case(*case)
    print(f"Generated EXACT 3 MODEL VISAS in {OUT}")


if __name__ == "__main__":
    main()
