"""Unit tests for Driving Licence adapter module."""

from app.adapters.driving_licence_adapter import (
    adapt_driving_licence_response,
    validate_dl_number,
)
from app.schemas import EvidenceType


def test_validate_dl_number_valid() -> None:
    res = validate_dl_number("MH1220150001234")
    assert res is not None
    assert res["format_valid"] is True
    assert res["state_code"] == "MH"


def test_validate_dl_number_invalid() -> None:
    res = validate_dl_number("INVALID123")
    assert res is not None
    assert res["format_valid"] is False


def test_adapt_driving_licence_response() -> None:
    raw = {
        "status": "completed",
        "visual_fields": {
            "dl_number": "DL0420191234567",
            "name": "VIKRAM SINGH",
            "dob": "1990-08-20",
            "issuing_authority": "RTO DELHI",
            "validity_date": "2035-08-19",
            "address": "123 CONNAUGHT PLACE NEW DELHI",
        },
        "quality": {"score": 92.5},
    }
    result = adapt_driving_licence_response(raw, document_id="dl.jpg")
    assert result.document.document_type == "Driving Licence"
    assert result.document.source_module == "driving_licence"
    assert result.document.processing_status == "completed"

    fields_found = {ev.field: ev.value for ev in result.evidence}
    assert fields_found["dl_number"] == "DL0420191234567"
    assert fields_found["name"] == "VIKRAM SINGH"
    assert fields_found["dob"] == "1990-08-20"
    assert fields_found["issuing_authority"] == "RTO DELHI"
    assert fields_found["validity_date"] == "2035-08-19"
    assert fields_found["address"] == "123 CONNAUGHT PLACE NEW DELHI"
    assert fields_found["dl_number_validation"]["format_valid"] is True

    for ev in result.evidence:
        if ev.field != "quality.score":
            assert ev.confidence is None
