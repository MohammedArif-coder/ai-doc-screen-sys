"""FastAPI entry point for the DAKSH P6 API."""

from pathlib import Path
import logging
import tempfile
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.case_service import CaseServiceResult, run_case
from app.services.decision_engine import make_decision
from app.services.risk_aggregator import aggregate_risk


logger = logging.getLogger(__name__)
app = FastAPI(title="DAKSH P6 API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def _model_dict(model: Any) -> dict[str, Any]:
    """Serialize a Pydantic model without exposing adapter raw responses."""

    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


def _public_case_data(case: CaseServiceResult) -> dict[str, Any]:
    evidence_by_document = {}
    for item in case.evidence:
        evidence_by_document.setdefault(item.document_id, []).append(
            item.evidence_id
        )

    contradictions = []
    for contradiction in case.contradictions:
        public_contradiction = _model_dict(contradiction)
        evidence_ids = []
        for evidence_id in (
            evidence_by_document.get(contradiction.document_a, [])
            + evidence_by_document.get(contradiction.document_b, [])
        ):
            if evidence_id in contradiction.explanation:
                evidence_ids.append(evidence_id)
        public_contradiction["evidence_ids"] = evidence_ids
        contradictions.append(public_contradiction)

    return {
        "documents": [
            _model_dict(document)
            for document in (
                case.passport_document,
                case.visa_document,
                case.aadhaar_document,
                case.driving_licence_document,
                case.pan_document,
            )
            if document is not None
        ],
        "evidence": [_model_dict(item) for item in case.evidence],
        "contradictions": contradictions,
        "adapter_errors": [
            f"{error.split(':', 1)[0]}: adapter processing failed"
            for error in case.adapter_errors
        ],
    }


async def _save_upload(upload: UploadFile, suffix: str) -> str:
    content = await upload.read()
    with tempfile.NamedTemporaryFile(
        mode="wb",
        suffix=suffix,
        prefix="daksh-",
        delete=False,
    ) as temporary_file:
        temporary_file.write(content)
        return temporary_file.name


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "DAKSH P6 API"}


@app.get("/api/system-status")
def system_status() -> dict[str, Any]:
    import requests

    services = {
        "aadhaar": {"port": 8001, "name": "Aadhaar Module", "status": "online"},
        "pan": {"port": 8005, "name": "PAN Module", "status": "online"},
        "dl": {"port": 8004, "name": "Driving Licence Module", "status": "online"},
        "passport": {"port": 8002, "name": "Passport Module", "status": "online"},
        "visa": {"port": 5000, "name": "Visa Module", "status": "online"},
    }

    for key, info in services.items():
        port = info["port"]
        try:
            r = requests.get(f"http://127.0.0.1:{port}/api/health", timeout=0.5)
            if r.ok:
                info["status"] = "online"
            else:
                info["status"] = "degraded"
        except Exception:
            info["status"] = "offline"

    return {
        "daksh_engine": "online",
        "api_mode": "real",
        "services": services,
    }


def _is_valid_upload(file_obj: Any) -> bool:
    return file_obj is not None and getattr(file_obj, "filename", None) is not None and bool(str(file_obj.filename).strip())


@app.post("/api/screen-case")
async def screen_case(
    passport: UploadFile | None = File(None),
    visa: UploadFile | None = File(None),
    aadhaar: UploadFile | None = File(None),
    driving_licence: UploadFile | None = File(None),
    pan: UploadFile | None = File(None),
) -> JSONResponse:
    passport_path: str | None = None
    visa_path: str | None = None
    aadhaar_path: str | None = None
    dl_path: str | None = None
    pan_path: str | None = None

    try:
        if _is_valid_upload(passport):
            passport_path = await _save_upload(
                passport,
                Path(passport.filename or "passport.jpg").suffix or ".jpg",
            )
        if _is_valid_upload(visa):
            visa_path = await _save_upload(
                visa,
                Path(visa.filename or "visa.jpg").suffix or ".jpg",
            )
        if _is_valid_upload(aadhaar):
            aadhaar_path = await _save_upload(
                aadhaar,
                Path(aadhaar.filename or "aadhaar.jpg").suffix or ".jpg",
            )
        if _is_valid_upload(driving_licence):
            dl_path = await _save_upload(
                driving_licence,
                Path(driving_licence.filename or "driving_licence.jpg").suffix or ".jpg",
            )
        if _is_valid_upload(pan):
            pan_path = await _save_upload(
                pan,
                Path(pan.filename or "pan.jpg").suffix or ".jpg",
            )

        if (
            passport_path is None
            and visa_path is None
            and aadhaar_path is None
            and dl_path is None
            and pan_path is None
        ):
            return JSONResponse(
                status_code=422,
                content={"error": "Upload at least one document to start screening."},
            )

        kwargs: dict[str, Any] = {}
        if aadhaar_path is not None:
            kwargs["aadhaar_image_path"] = aadhaar_path
        if dl_path is not None:
            kwargs["driving_licence_image_path"] = dl_path
        if pan_path is not None:
            kwargs["pan_image_path"] = pan_path

        case = run_case(passport_path, visa_path, **kwargs)

        def _is_failed(res: Any) -> bool:
            return res is None or (getattr(res, "error", None) is not None and not getattr(res, "evidence", None))

        passport_failed = (passport_path is None) or _is_failed(case.passport_result)
        visa_failed = (visa_path is None) or _is_failed(case.visa_result)
        aadhaar_failed = (aadhaar_path is None) or _is_failed(case.aadhaar_result)
        dl_failed = (dl_path is None) or _is_failed(case.driving_licence_result)
        pan_failed = (pan_path is None) or _is_failed(case.pan_result)

        if passport_failed and visa_failed and aadhaar_failed and dl_failed and pan_failed:
            error_message = "All submitted document processing failed."
            if (
                passport_path is not None
                and visa_path is not None
                and aadhaar_path is None
                and dl_path is None
                and pan_path is None
            ):
                error_message = "Both Passport and Visa processing failed."
            return JSONResponse(
                status_code=422,
                content={
                    "error": error_message,
                    **_public_case_data(case),
                },
            )

        if case.adapter_errors:
            logger.warning(
                "DAKSH adapter processing errors: %s",
                "; ".join(case.adapter_errors),
            )

        assessment = aggregate_risk(case.evidence, case.contradictions)
        decision = make_decision(assessment)
        response = _model_dict(decision)
        response["case_id"] = f"DAKSH-{uuid4().hex[:12].upper()}"
        response.update(_public_case_data(case))
        return JSONResponse(status_code=200, content=response)
    except Exception:
        logger.exception("DAKSH case processing failed")
        return JSONResponse(
            status_code=500,
            content={"error": "DAKSH case processing failed."},
        )
    finally:
        for path in (passport_path, visa_path, aadhaar_path, dl_path, pan_path):
            if path is not None:
                try:
                    Path(path).unlink(missing_ok=True)
                except OSError:
                    pass
