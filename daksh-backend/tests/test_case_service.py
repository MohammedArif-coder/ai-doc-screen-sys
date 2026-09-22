import unittest
from pathlib import Path

from app.adapters.passport_adapter import PassportAdapterResult
from app.adapters.visa_adapter import VisaAdapterResult
from app.schemas import Document, Evidence, EvidenceType
from app.services.case_service import run_case


def _document(document_id: str, document_type: str, module: str) -> Document:
    return Document(
        document_id=document_id,
        document_type=document_type,
        source_module=module,
        processing_status="completed",
    )


def _evidence(
    evidence_id: str,
    document_id: str,
    field: str,
    value: str,
    source: str,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field=field,
        value=value,
        confidence=None,
        source=source,
    )


class CaseServiceTests(unittest.TestCase):
    def test_both_adapters_merge_evidence_and_call_engine(self) -> None:
        passport_evidence = _evidence(
            "p-number", "passport-1", "passport_number", "A12345678",
            "passport.visual_fields",
        )
        visa_evidence = _evidence(
            "v-number", "visa-1", "passport_no", "A12345678", "visa.ocr",
        )
        passport = PassportAdapterResult(
            document=_document("passport-1", "Passport", "passport"),
            evidence=[passport_evidence],
        )
        visa = VisaAdapterResult(
            document=_document("visa-1", "Visa", "visa"),
            evidence=[visa_evidence],
        )
        observed: list[list[Evidence]] = []

        result = run_case(
            "passport.png",
            "visa.png",
            passport_runner=lambda _: passport,
            visa_runner=lambda _: visa,
            contradiction_detector=lambda evidence: (
                observed.append(evidence) or []
            ),
        )

        self.assertEqual(result.evidence, [passport_evidence, visa_evidence])
        self.assertEqual(observed, [[passport_evidence, visa_evidence]])
        self.assertEqual(result.contradictions, [])
        self.assertEqual(result.adapter_errors, [])

    def test_matching_and_mismatching_values(self) -> None:
        passport = PassportAdapterResult(
            document=_document("passport-1", "Passport", "passport"),
            evidence=[
                _evidence(
                    "p-number", "passport-1", "passport_number",
                    "A12345678", "passport.visual_fields",
                )
            ],
        )
        matching_visa = VisaAdapterResult(
            document=_document("visa-1", "Visa", "visa"),
            evidence=[
                _evidence(
                    "v-number", "visa-1", "passport_no",
                    "a12345678", "visa.ocr",
                )
            ],
        )
        mismatch_visa = VisaAdapterResult(
            document=matching_visa.document,
            evidence=[
                _evidence(
                    "v-number", "visa-1", "passport_no",
                    "B98765432", "visa.ocr",
                )
            ],
        )

        matching = run_case(
            "passport.png",
            "visa.png",
            passport_runner=lambda _: passport,
            visa_runner=lambda _: matching_visa,
        )
        mismatch = run_case(
            "passport.png",
            "visa.png",
            passport_runner=lambda _: passport,
            visa_runner=lambda _: mismatch_visa,
        )

        self.assertEqual(matching.contradictions, [])
        self.assertEqual(len(mismatch.contradictions), 1)
        self.assertEqual(mismatch.contradictions[0].severity, "HIGH")
        self.assertIsNone(mismatch.contradictions[0].confidence)

    def test_failed_adapter_preserves_successful_result(self) -> None:
        visa = VisaAdapterResult(
            document=_document("visa-1", "Visa", "visa"),
            evidence=[
                _evidence(
                    "v-name", "visa-1", "applicant_name",
                    "John Kumar", "visa.ocr",
                )
            ],
        )

        result = run_case(
            "missing-passport.png",
            "visa.png",
            passport_runner=lambda _: (_ for _ in ()).throw(
                RuntimeError("service unavailable")
            ),
            visa_runner=lambda _: visa,
        )

        self.assertIsNone(result.passport_result)
        self.assertIs(result.visa_result, visa)
        self.assertEqual(result.evidence, visa.evidence)
        self.assertEqual(len(result.adapter_errors), 1)
        self.assertIn("service unavailable", result.adapter_errors[0])
        self.assertEqual(result.contradictions, [])

    def test_no_final_status_or_risk_decision_is_created(self) -> None:
        result = run_case(
            Path("passport.png"),
            Path("visa.png"),
            passport_runner=lambda _: PassportAdapterResult(
                document=_document("p", "Passport", "passport")
            ),
            visa_runner=lambda _: VisaAdapterResult(
                document=_document("v", "Visa", "visa")
            ),
        )

        self.assertFalse(hasattr(result, "status"))
        self.assertFalse(hasattr(result, "risk_score"))
        self.assertFalse(hasattr(result, "fraud_probability"))


if __name__ == "__main__":
    unittest.main()
