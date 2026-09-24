"""Generate clear synthetic sample documents for DAKSH demonstration."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
OUTPUT_DIR.mkdir(exist_ok=True)

def draw_header(draw, title, bg_color):
    draw.rectangle([0, 0, 800, 80], fill=bg_color)
    draw.text((30, 25), title, fill="white")

def create_synthetic_passport(filename, passport_num="Z8942103", name="RAHUL SHARMA", dob="15/06/1995"):
    img = Image.new("RGB", (800, 500), color="#F4F6F9")
    draw = ImageDraw.Draw(img)
    
    # Header
    draw_header(draw, "REPUBLIC OF INDIA - PASSPORT", "#1A365D")
    
    # Details
    draw.rectangle([30, 100, 200, 320], fill="#CBD5E1", outline="#64748B", width=2)
    draw.text((65, 200), "PHOTO", fill="#475569")
    
    text_items = [
        ("Type / Type", "P"),
        ("Country Code / Code", "IND"),
        ("Passport No. / Passport No.", passport_num),
        ("Surname & Given Name", name),
        ("Nationality", "INDIAN"),
        ("Date of Birth", dob),
        ("Sex", "M"),
    ]
    
    y = 100
    for label, val in text_items:
        draw.text((220, y), label, fill="#64748B")
        draw.text((420, y), val, fill="#0F172A")
        y += 32
        
    # MRZ Zone
    draw.rectangle([20, 390, 780, 480], fill="#E2E8F0", outline="#94A3B8")
    mrz1 = f"P<INDSURNAMENUMBER<<{name.replace(' ', '<')}<<<<<<<<<<<<<"
    mrz2 = f"{passport_num}4IND9506152M3001018<<<<<<<<<<<<<<04"
    draw.text((40, 405), mrz1[:44], fill="#1E293B")
    draw.text((40, 440), mrz2[:44], fill="#1E293B")
    
    img.save(OUTPUT_DIR / filename, "JPEG", quality=95)
    print(f"Generated {filename}")

def create_synthetic_visa(filename, passport_num="Z8942103", name="RAHUL SHARMA"):
    img = Image.new("RGB", (800, 500), color="#F8FAFC")
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "ENTRY VISA - UNITED STATES / Schengen", "#065F46")
    
    draw.rectangle([30, 100, 180, 280], fill="#CBD5E1", outline="#64748B", width=2)
    draw.text((55, 180), "PHOTO", fill="#475569")
    
    items = [
        ("Visa Type / Category", "C - TOURIST"),
        ("Passport No.", passport_num),
        ("Full Name", name),
        ("Valid From", "01/01/2026"),
        ("Until", "01/01/2027"),
        ("Entries", "MULTIPLE"),
    ]
    
    y = 110
    for label, val in items:
        draw.text((200, y), label, fill="#64748B")
        draw.text((400, y), val, fill="#0F172A")
        y += 35
        
    img.save(OUTPUT_DIR / filename, "JPEG", quality=95)
    print(f"Generated {filename}")

def create_synthetic_aadhaar(filename, name="RAHUL SHARMA", dob="15/06/1995", blurry=False):
    img = Image.new("RGB", (800, 500), color="#FFFFFF")
    draw = ImageDraw.Draw(img)
    
    draw_header(draw, "UNIQUE IDENTIFICATION AUTHORITY OF INDIA", "#991B1B")
    
    draw.rectangle([40, 110, 180, 290], fill="#E2E8F0", outline="#94A3B8")
    draw.text((70, 190), "PHOTO", fill="#475569")
    
    items = [
        ("Name", name),
        ("DOB", dob),
        ("Gender", "MALE"),
        ("Aadhaar No.", "XXXX XXXX 4819"),
    ]
    
    y = 120
    for label, val in items:
        draw.text((210, y), f"{label}:", fill="#475569")
        draw.text((320, y), val, fill="#000000")
        y += 40
        
    # QR Code placeholder
    draw.rectangle([580, 120, 750, 290], fill="#000000")
    draw.rectangle([600, 140, 730, 270], fill="#FFFFFF")
    draw.text((615, 195), "QR CODE", fill="#000000")
    
    if blurry:
        img = img.filter(ImageFilter.GaussianBlur(radius=6))
        
    img.save(OUTPUT_DIR / filename, "JPEG", quality=95)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_synthetic_passport("01_PASSPORT_MATCH.jpg", "Z8942103", "RAHUL SHARMA", "15/06/1995")
    create_synthetic_visa("01_VISA_MATCH.jpg", "Z8942103", "RAHUL SHARMA")
    create_synthetic_aadhaar("01_AADHAAR_MATCH.jpg", "RAHUL SHARMA", "15/06/1995")

    create_synthetic_passport("02_PASSPORT_DOB_ALTERED.jpg", "Z8942103", "RAHUL SHARMA", "15/06/1990")
    create_synthetic_visa("02_VISA_MATCH.jpg", "Z8942103", "RAHUL SHARMA")
    create_synthetic_aadhaar("02_AADHAAR_MATCH.jpg", "RAHUL SHARMA", "15/06/1995")

    create_synthetic_passport("03_PASSPORT_MISMATCH.jpg", "Z8942103", "RAHUL SHARMA", "15/06/1990")
    create_synthetic_visa("03_VISA_MISMATCH.jpg", "X9999999", "RAHUL SMITH")
    create_synthetic_aadhaar("03_AADHAAR_MISMATCH.jpg", "RAHUL SHARMA", "20/12/1988")

    create_synthetic_aadhaar("04_AADHAAR_POOR_QUALITY.jpg", "RAHUL SHARMA", "15/06/1995", blurry=True)
