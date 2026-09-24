from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import shutil
import uuid

from app.modules.driving_license.module import process_driving_license


router = APIRouter()


# Upload folder
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/api/screen")
async def screen_document(
    file: UploadFile = File(...)
):
    """
    Upload a document and screen it.

    Currently supports:
    Driving Licence
    """

    # Allowed image types
    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/jpg"
    ]

    # Check file type
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported."
        )

    # Get file extension
    file_extension = Path(file.filename).suffix

    # Create unique filename
    unique_filename = (
        f"{uuid.uuid4()}{file_extension}"
    )

    # Complete upload path
    file_path = UPLOAD_DIR / unique_filename

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            file.file,
            buffer
        )

    try:

        # Process the uploaded Driving Licence
        result = process_driving_license(
            str(file_path)
        )

        return {
            "success": True,
            "filename": file.filename,
            "result": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )