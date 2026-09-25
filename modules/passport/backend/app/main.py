from pathlib import Path
from uuid import uuid4
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi import FastAPI, UploadFile, File, HTTPException

from app.passport.screening import screen_passport


app = FastAPI(
    title="DAKSH Passport Screening API"
)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


@app.get("/")
def home():
    return FileResponse("app/static/index.html")


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "module": "passport"
    }


@app.post("/api/passport/screen")
async def screen_passport_api(
    file: UploadFile = File(...)
):

    allowed_types = {
        "image/jpeg",
        "image/png",
        "image/jpg"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported."
        )

    upload_dir = Path(
        "app/passport/artifacts/uploads"
    )

    upload_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    extension = ".jpg"

    if file.content_type == "image/png":
        extension = ".png"

    file_path = upload_dir / (
        f"{uuid4().hex}{extension}"
    )

    try:

        with open(file_path, "wb") as buffer:

            while chunk := await file.read(1024 * 1024):

                buffer.write(chunk)

        result = screen_passport(
            file_path
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )