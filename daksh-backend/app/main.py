"""FastAPI entry point for the DAKSH P6 screening pipeline."""

from pathlib import Path
import tempfile
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.services.case_service import CaseServiceResult, run_case
from app.services.decision_engine import make_decision
from app.services.risk_aggregator import aggregate_risk


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


@app.post("/api/screen-case")
async def screen_case(
    passport: UploadFile | None = File(None),
    visa: UploadFile | None = File(None),
    aadhaar: UploadFile | None = File(None),
) -> JSONResponse:
    passport_path: str | None = None
    visa_path: str | None = None
    aadhaar_path: str | None = None
    try:
        if passport is not None:
            passport_path = await _save_upload(
                passport,
                Path(passport.filename or "passport.jpg").suffix or ".jpg",
            )
        if visa is not None:
            visa_path = await _save_upload(
                visa,
                Path(visa.filename or "visa.jpg").suffix or ".jpg",
            )
        if aadhaar is not None:
            aadhaar_path = await _save_upload(
                aadhaar,
                Path(aadhaar.filename or "aadhaar.jpg").suffix or ".jpg",
            )

        if passport_path is None and visa_path is None and aadhaar_path is None:
            return JSONResponse(
                status_code=422,
                content={"error": "Upload at least one document to start screening."},
            )

        case = run_case(
            passport_path,
            visa_path,
            aadhaar_image_path=aadhaar_path,
        )
        if (
            case.passport_result is None
            and case.visa_result is None
            and case.aadhaar_result is None
        ):
            return JSONResponse(
                status_code=422,
                content={
                    "error": (
                        "All submitted document processing failed."
                    ),
                    **_public_case_data(case),
                },
            )

        assessment = aggregate_risk(case.evidence, case.contradictions)
        decision = make_decision(assessment)
        response = _model_dict(decision)
        response["case_id"] = f"DAKSH-{uuid4().hex[:12].upper()}"
        response.update(_public_case_data(case))
        return JSONResponse(status_code=200, content=response)
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "DAKSH case processing failed."},
        )
    finally:
        for path in (passport_path, visa_path, aadhaar_path):
            if path is not None:
                try:
                    Path(path).unlink(missing_ok=True)
                except OSError:
                    pass
