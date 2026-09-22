import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.adapters.aadhaar_adapter import (
    adapt_aadhaar_response,
    screen_aadhaar_file,
)
from app.schemas import EvidenceType


COMPLETE_RESPONSE = {
    "case_id": "CASE-AAD-001",
    "module_status": "COMPLETE",
    "fields": {
        "name": {
            "value": "Aarav Kumar",
            "normalized_value": "Aarav Kumar",
            "confidence": 0.92,
            "confidence_basis": "OCR_ENGINE",
            "bounding_box": [10, 20, 100, 30],
            "page": 1,
        },
        "dob": {
            "value": "12/04/2005",
            "normalized_value": "2005-04-12",
            "confidence": None,
            "confidence_basis": "OCR_ENGINE",
        },
        "aadhaar_number": {
            "value": "304332181964",
            "normalized_value": "304332181964",
            "confidence": 0.88,
        },
    },
    "document_identification": {"result": "AADHAAR", "confidence": 0.85},
    "quality": {"overall_score": 90, "overall_label": "GOOD"},
    "orientation": {"applied_rotation": 0, "confidence": 0.8},
    "photo": {"status": "DETECTED", "quality_score": 75},
    "metadata": {"editing_software_detected": False},
    "number_validation": {
        "format_status": "FORMAT_VALID",
        "checksum_status": "CHECKSUM_VALID",
    },
    "qr": {
        "status": "QR_PRESENT",
        "decoded": True,
        "fields": {"name": "Aarav Kumar", "yob": "2005"},
    },
    "offline_ekyc": {
        "provided": True,
        "status": "PARSED",
        "signature_status": "NOT_CONFIGURED",
        "fields": {"name": "Aarav Kumar"},
    },
    "qr_consistency": {"checked": True, "overall": "MATCH"},
    "validation": [{"check": "checksum", "status": "CHECKSUM_VALID"}],
    "contradictions": [],
    "evidence_relations": [],
    "forensics": {
        "analyzed": True,
        "overall_label": "SUSPICIOUS",
        "regions": [
            {
                "region_id": "FOR-001",
                "reason": "Localized anomaly",
                "severity": "MEDIUM",
                "confidence": 0.6,
                "confidence_basis": "HEURISTIC",
                "bounding_box": [1, 2, 30, 40],
            }
        ],
    },
    "evidence": [],
    "scores": {"integrity_score": 90, "coverage_sufficient": True},
    "screening": {
        "status": "CLEAR",
        "headline": "Module screening completed",
        "reasons": [{"text": "Available evidence is consistent."}],
    },
    "errors": [],
}


class AadhaarAdapterTests(unittest.TestCase):
    def test_complete_response_mapping(self) -> None:
        result = adapt_aadhaar_response(
            COMPLETE_RESPONSE,
            document_id="CASE-AAD-001",
        )
        self.assertEqual(result.document.document_type, "Aadhaar")
        self.assertEqual(result.document.document_id, "CASE-AAD-001")
        self.assertGreaterEqual(len(result.evidence), 20)
        self.assertIs(result.raw_response, COMPLETE_RESPONSE)

    def test_field_provenance_and_normalization(self) -> None:
        result = adapt_aadhaar_response(
            COMPLETE_RESPONSE,
            document_id="CASE-AAD-001",
        )
        name = next(item for item in result.evidence if item.field == "printed.name")
        dob = next(item for item in result.evidence if item.field == "printed.dob")
        self.assertEqual(name.confidence, 0.92)
        self.assertEqual(dob.normalized_value, "2005-04-12")
        self.assertIsNone(dob.confidence)

    def test_derived_validation_and_qr_are_not_authority_verification(self) -> None:
        result = adapt_aadhaar_response(
            COMPLETE_RESPONSE,
            document_id="CASE-AAD-001",
        )
        checksum = next(
            item for item in result.evidence if item.field == "number_validation"
        )
        qr = next(item for item in result.evidence if item.field == "qr.status")
        qr_name = next(item for item in result.evidence if item.field == "qr.name")
        signature = next(
            item
            for item in result.evidence
            if item.field == "offline_ekyc.signature_status"
        )
        self.assertEqual(checksum.evidence_type, EvidenceType.DERIVED)
        self.assertEqual(qr.evidence_type, EvidenceType.OBSERVATION)
        self.assertEqual(qr_name.source, "aadhaar.qr")
        self.assertEqual(signature.value, "NOT_CONFIGURED")

    def test_forensics_preserve_confidence_without_fake_label(self) -> None:
        result = adapt_aadhaar_response(
            COMPLETE_RESPONSE,
            document_id="CASE-AAD-001",
        )
        forensic = next(
            item
            for item in result.evidence
            if item.field == "forensics.region[0]"
        )
        self.assertEqual(forensic.confidence, 0.6)
        self.assertNotIn("FAKE", str(forensic.value))

    def test_screening_status_is_not_daksh_decision(self) -> None:
        result = adapt_aadhaar_response(
            COMPLETE_RESPONSE,
            document_id="CASE-AAD-001",
        )
        screening = next(
            item for item in result.evidence if item.field == "screening.status"
        )
        self.assertEqual(screening.value, "CLEAR")
        self.assertNotEqual(screening.field, "status")

    def test_missing_sections_and_module_failure(self) -> None:
        response = {
            "case_id": "CASE-FAILED",
            "module_status": "FAILED",
            "screening": {"status": "INCONCLUSIVE"},
            "errors": [{"stage": "ocr", "message": "unavailable"}],
        }
        result = adapt_aadhaar_response(response, document_id="CASE-FAILED")
        self.assertEqual(result.document.processing_status, "FAILED")
        self.assertEqual(result.error, "Aadhaar module returned errors.")
        self.assertFalse(any(item.severity for item in result.evidence))

    def test_http_upload_and_raw_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aadhaar.png"
            path.write_bytes(b"\x89PNG\r\n\x1a\nmock")
            mocked_response = Mock(status_code=200)
            mocked_response.json.return_value = COMPLETE_RESPONSE
            with patch(
                "app.adapters.aadhaar_adapter.requests.post",
                return_value=mocked_response,
            ) as post:
                result = screen_aadhaar_file(path, base_url="http://test")
        self.assertEqual(result.document.document_id, "CASE-AAD-001")
        self.assertIs(result.raw_response, COMPLETE_RESPONSE)
        self.assertEqual(post.call_args.kwargs["data"]["persist_artifacts"], "false")
        self.assertIn("document", post.call_args.kwargs["files"])

    def test_http_errors_are_graceful(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "aadhaar.png"
            path.write_bytes(b"\x89PNG\r\n\x1a\nmock")
            mocked_response = Mock(status_code=503)
            mocked_response.json.return_value = {"error": "unavailable"}
            with patch(
                "app.adapters.aadhaar_adapter.requests.post",
                return_value=mocked_response,
            ):
                result = screen_aadhaar_file(path, base_url="http://test")
        self.assertIn("HTTP 503", result.error)
        self.assertEqual(result.raw_response, {"error": "unavailable"})


if __name__ == "__main__":
    unittest.main()
