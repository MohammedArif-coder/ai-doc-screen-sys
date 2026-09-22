from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.adapters.passport_adapter import PassportAdapterResult
from app.adapters.visa_adapter import VisaAdapterResult
from app.adapters.aadhaar_adapter import AadhaarAdapterResult
from app.main import app
from app.schemas import Contradiction, Document, Evidence, EvidenceType
from app.services.case_service import CaseServiceResult


client = TestClient(app)


def _document(document_id: str, document_type: str, module: str) -> Document:
    return Document(
        document_id=document_id,
        document_type=document_type,
        source_module=module,
        processing_status="completed",
    )


def _evidence(evidence_id: str, document_id: str, field: str) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field=field,
        value="different",
        confidence=None,
        source="test",
    )


def _case(
    passport_result=None,
    visa_result=None,
    aadhaar_result=None,
    errors=None,
) -> CaseServiceResult:
    passport_result = passport_result or PassportAdapterResult(
        document=_document("passport-1", "Passport", "passport"),
        evidence=[_evidence("e-passport", "passport-1", "passport_number")],
    )
    visa_result = visa_result or VisaAdapterResult(
        document=_document("visa-1", "Visa", "visa"),
        evidence=[_evidence("e-visa", "visa-1", "passport_no")],
    )
    return CaseServiceResult(
        passport_result=passport_result,
        visa_result=visa_result,
        passport_document=passport_result.document if passport_result else None,
        visa_document=visa_result.document if visa_result else None,
        aadhaar_result=aadhaar_result,
        aadhaar_document=(
            aadhaar_result.document if aadhaar_result else None
        ),
        evidence=(
            (passport_result.evidence if passport_result else [])
            + (visa_result.evidence if visa_result else [])
            + (aadhaar_result.evidence if aadhaar_result else [])
        ),
        contradictions=[],
        adapter_errors=errors or [],
    )


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_screen_case_returns_decision_and_sanitized_case_data() -> None:
    with patch("app.main.run_case", return_value=_case()):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"passport-bytes", "image/jpeg"),
                "visa": ("visa.jpg", b"visa-bytes", "image/jpeg"),
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "CLEAR"
    assert body["review_required"] is False
    assert body["headline"]
    assert len(body["documents"]) == 2
    assert body["evidence"][0]["evidence_id"] == "e-passport"
    assert "raw_response" not in body


def test_screen_case_accepts_optional_aadhaar_and_returns_all_documents() -> None:
    aadhaar = AadhaarAdapterResult(
        document=_document("aadhaar-1", "Aadhaar", "aadhaar"),
        evidence=[_evidence("e-aadhaar", "aadhaar-1", "printed.name")],
    )
    case = _case(aadhaar_result=aadhaar)
    captured: dict[str, str | None] = {}

    def mocked_run_case(
        passport_path: str,
        visa_path: str,
        *,
        aadhaar_image_path: str | None = None,
    ) -> CaseServiceResult:
        captured["passport"] = passport_path
        captured["visa"] = visa_path
        captured["aadhaar"] = aadhaar_image_path
        return case

    with patch("app.main.run_case", side_effect=mocked_run_case):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"passport", "image/jpeg"),
                "visa": ("visa.jpg", b"visa", "image/jpeg"),
                "aadhaar": ("aadhaar.jpg", b"aadhaar", "image/jpeg"),
            },
        )

    assert response.status_code == 200
    assert {item["document_id"] for item in response.json()["documents"]} == {
        "passport-1",
        "visa-1",
        "aadhaar-1",
    }
    assert response.json()["evidence"][-1]["evidence_id"] == "e-aadhaar"
    assert captured["aadhaar"] is not None
    assert all(
        not Path(path).exists()
        for path in captured.values()
        if path is not None
    )


def test_screen_case_passes_aadhaar_contradiction_to_decision() -> None:
    aadhaar = AadhaarAdapterResult(
        document=_document("aadhaar-1", "Aadhaar", "aadhaar"),
        evidence=[_evidence("e-aadhaar", "aadhaar-1", "printed.dob")],
    )
    case = _case(aadhaar_result=aadhaar)
    case.contradictions = [
        Contradiction(
            contradiction_id="c-aadhaar-dob",
            field="dob",
            document_a="passport-1",
            document_b="aadhaar-1",
            value_a="2005-04-12",
            value_b="2005-04-13",
            comparison="MISMATCH",
            severity="HIGH",
            explanation="The date of birth differs.",
        )
    ]
    with patch("app.main.run_case", return_value=case):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"passport", "image/jpeg"),
                "visa": ("visa.jpg", b"visa", "image/jpeg"),
                "aadhaar": ("aadhaar.jpg", b"aadhaar", "image/jpeg"),
            },
        )

    assert response.status_code == 200
    assert response.json()["status"] == "HIGH_REVIEW"
    assert response.json()["supporting_contradiction_ids"] == [
        "c-aadhaar-dob"
    ]


def test_screen_case_aadhaar_failure_preserves_other_documents_and_cleans_up() -> None:
    failed_aadhaar = AadhaarAdapterResult(
        document=_document("aadhaar-1", "Aadhaar", "aadhaar"),
        error="Aadhaar service unavailable",
    )
    case = _case(aadhaar_result=failed_aadhaar, errors=["aadhaar: failed"])
    captured_paths: list[str] = []

    def mocked_run_case(
        passport_path: str,
        visa_path: str,
        *,
        aadhaar_image_path: str | None = None,
    ) -> CaseServiceResult:
        captured_paths.extend(
            path for path in (passport_path, visa_path, aadhaar_image_path)
            if path is not None
        )
        return case

    with patch("app.main.run_case", side_effect=mocked_run_case):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"passport", "image/jpeg"),
                "visa": ("visa.jpg", b"visa", "image/jpeg"),
                "aadhaar": ("aadhaar.jpg", b"aadhaar", "image/jpeg"),
            },
        )

    assert response.status_code == 200
    assert {item["document_id"] for item in response.json()["documents"]} == {
        "passport-1",
        "visa-1",
        "aadhaar-1",
    }
    assert response.json()["adapter_errors"] == [
        "aadhaar: adapter processing failed"
    ]
    assert all(not Path(path).exists() for path in captured_paths)


def test_contradiction_ids_reach_final_response() -> None:
    case = _case()
    case.contradictions = [
        Contradiction(
            contradiction_id="c-passport-number",
            field="passport_number",
            document_a="passport-1",
            document_b="visa-1",
            value_a="A123",
            value_b="B456",
            comparison="MISMATCH",
            severity="HIGH",
            explanation="The values differ.",
        )
    ]
    with patch("app.main.run_case", return_value=case):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"x", "image/jpeg"),
                "visa": ("visa.jpg", b"y", "image/jpeg"),
            },
        )
    assert response.status_code == 200
    assert response.json()["supporting_contradiction_ids"] == [
        "c-passport-number"
    ]


def test_adapter_failure_is_structured_and_files_are_cleaned_up() -> None:
    case = _case(errors=["passport: service unavailable"])
    captured_paths: list[str] = []

    def mocked_run_case(passport_path: str, visa_path: str) -> CaseServiceResult:
        captured_paths.extend([passport_path, visa_path])
        return case

    with patch("app.main.run_case", side_effect=mocked_run_case):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"x", "image/jpeg"),
                "visa": ("visa.jpg", b"y", "image/jpeg"),
            },
        )

    assert response.status_code == 200
    assert response.json()["adapter_errors"] == [
        "passport: adapter processing failed"
    ]
    assert response.json()["status"] == "CLEAR"
    assert all(not Path(path).exists() for path in captured_paths)


def test_both_adapter_failures_return_processing_error() -> None:
    failed = CaseServiceResult(
        passport_result=None,
        visa_result=None,
        passport_document=None,
        visa_document=None,
        adapter_errors=["passport: failed", "visa: failed"],
    )
    with patch("app.main.run_case", return_value=failed):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"x", "image/jpeg"),
                "visa": ("visa.jpg", b"y", "image/jpeg"),
            },
        )
    assert response.status_code == 422
    assert "Both Passport and Visa processing failed." in response.json()["error"]


def test_no_prohibited_outputs() -> None:
    with patch("app.main.run_case", return_value=_case()):
        response = client.post(
            "/api/screen-case",
            files={
                "passport": ("passport.jpg", b"x", "image/jpeg"),
                "visa": ("visa.jpg", b"y", "image/jpeg"),
            },
        )
    body_text = str(response.json()).casefold()
    for prohibited in (
        "fraud_probability",
        "authenticity_percentage",
        "fake",
        "genuine",
    ):
        assert prohibited not in body_text
