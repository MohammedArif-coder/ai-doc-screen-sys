"""Generate distinct sample images for a new person (PRIYA VERMA) to test Task 2."""

from pathlib import Path
from PIL import Image, ImageDraw

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "sample_documents"
OUTPUT_DIR.mkdir(exist_ok=True)

def create_new_dl(filename):
    img = Image.new("RGB", (800, 500), color="#FFFBEB")
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, 800, 80], fill="#D97706")
    draw.text((30, 25), "KARNATAKA RTO - DRIVING LICENCE", fill="white")
    
    draw.rectangle([30, 100, 180, 280], fill="#E2E8F0", outline="#94A3B8")
    draw.text((55, 180), "PHOTO", fill="#475569")
    
    items = [
        ("DL No.", "KA0120220099887"),
        ("Name", "PRIYA VERMA"),
        ("DOB", "25/11/1998"),
        ("Authority", "RTO BANGALORE CENTRAL"),
        ("Valid Till", "24/11/2038"),
        ("Address", "88 INDIRANAGAR BANGALORE"),
    ]
    
    y = 110
    for label, val in items:
        draw.text((200, y), f"{label}:", fill="#475569")
        draw.text((320, y), val, fill="#000000")
        y += 35
        
    img.save(OUTPUT_DIR / filename, "JPEG", quality=95)
    print(f"Generated {filename}")

def create_new_pan(filename):
    img = Image.new("RGB", (800, 500), color="#FDF2F8")
    draw = ImageDraw.Draw(img)
    
    draw.rectangle([0, 0, 800, 80], fill="#BE185D")
    draw.text((30, 25), "INCOME TAX DEPARTMENT - GOVT OF INDIA", fill="white")
    
    draw.rectangle([30, 100, 180, 280], fill="#E2E8F0", outline="#94A3B8")
    draw.text((55, 180), "PHOTO", fill="#475569")
    
    items = [
        ("PAN No.", "XYZPK1122Q"),
        ("Name", "PRIYA VERMA"),
        ("Father's Name", "VIKAS VERMA"),
        ("DOB", "25/11/1998"),
    ]
    
    y = 120
    for label, val in items:
        draw.text((200, y), f"{label}:", fill="#475569")
        draw.text((320, y), val, fill="#000000")
        y += 40
        
    img.save(OUTPUT_DIR / filename, "JPEG", quality=95)
    print(f"Generated {filename}")

if __name__ == "__main__":
    create_new_dl("05_DL_PRIYA_VERMA.jpg")
    create_new_pan("05_PAN_PRIYA_VERMA.jpg")
