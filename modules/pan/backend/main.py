"""FastAPI application wrapper for DAKSH PAN Module."""

from pathlib import Path
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from pan_pipeline import run_pan_pipeline

app = FastAPI(
    title="DAKSH PAN Screening API",
    description="PAN Card Authentication & Screening Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def home():
    return {"message": "DAKSH PAN Screening Service is Running"}


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "DAKSH PAN Module"}


@app.post("/api/pan/screen")
@app.post("/api/screen")
async def screen_pan(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/jpg"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported."
        )

    file_extension = Path(file.filename or "pan.jpg").suffix or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = run_pan_pipeline(str(file_path))
        return {
            "success": True,
            "filename": file.filename,
            "result": result,
            "fields": result.get("fields", {}),
            "visual_fields": result.get("fields", {}),
            "status": "completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass
