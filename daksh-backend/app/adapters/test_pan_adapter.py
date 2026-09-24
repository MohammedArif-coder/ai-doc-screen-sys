"""Unit tests for PAN Card adapter module."""

from app.adapters.pan_adapter import (
    adapt_pan_response,
    validate_pan_number,
)
from app.schemas import EvidenceType


def test_validate_pan_number_valid() -> None:
    res = validate_pan_number("ABCDE1234F")
    assert res is not None
    assert res["format_valid"] is True
    assert res["entity_code"] == "D"


def test_validate_pan_number_individual() -> None:
    res = validate_pan_number("ABCPD1234F")
    assert res is not None
    assert res["format_valid"] is True
    assert res["entity_code"] == "P"
    assert res["entity_type"] == "Individual / Person"


def test_validate_pan_number_invalid() -> None:
    res = validate_pan_number("12345ABCDE")
    assert res is not None
    assert res["format_valid"] is False


def test_adapt_pan_response() -> None:
    raw = {
        "status": "completed",
        "visual_fields": {
            "pan_number": "ABCPK9876M",
            "name": "KAVITA MEHTA",
            "dob": "1994-03-12",
            "father_name": "SURESH MEHTA",
        },
        "quality": {"score": 96.0},
    }
    result = adapt_pan_response(raw, document_id="pan.jpg")
    assert result.document.document_type == "PAN"
    assert result.document.source_module == "pan"
    assert result.document.processing_status == "completed"

    fields_found = {ev.field: ev.value for ev in result.evidence}
    assert fields_found["pan_number"] == "ABCPK9876M"
    assert fields_found["name"] == "KAVITA MEHTA"
    assert fields_found["dob"] == "1994-03-12"
    assert fields_found["father_name"] == "SURESH MEHTA"
    assert fields_found["pan_number_validation"]["format_valid"] is True
    assert fields_found["pan_number_validation"]["entity_type"] == "Individual / Person"

    for ev in result.evidence:
        if ev.field != "quality.score":
            assert ev.confidence is None
