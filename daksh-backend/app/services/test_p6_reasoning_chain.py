import unittest

from app.adapters.aadhaar_adapter import AadhaarAdapterResult
from app.adapters.passport_adapter import PassportAdapterResult
from app.adapters.visa_adapter import VisaAdapterResult
from app.schemas import Document, Evidence, EvidenceType, ScreeningStatus
from app.services.case_service import run_case
from app.services.decision_engine import make_decision
from app.services.risk_aggregator import aggregate_risk


def _document(document_id: str, document_type: str, source_module: str) -> Document:
    return Document(
        document_id=document_id,
        document_type=document_type,
        source_module=source_module,
        processing_status="completed",
    )


def _evidence(
    evidence_id: str,
    document_id: str,
    field: str,
    value: object,
    source: str,
    *,
    confidence: float | None = None,
    quality: float | None = None,
    severity: str | None = None,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field=field,
        value=value,
        confidence=confidence,
        quality=quality,
        severity=severity,
        source=source,
    )


def _passport(evidence: list[Evidence]) -> PassportAdapterResult:
    return PassportAdapterResult(
        document=_document("passport-1", "Passport", "passport"),
        evidence=evidence,
    )


def _visa(evidence: list[Evidence] | None = None) -> VisaAdapterResult:
    return VisaAdapterResult(
        document=_document("visa-1", "Visa", "visa"),
        evidence=evidence or [],
    )


def _aadhaar(evidence: list[Evidence]) -> AadhaarAdapterResult:
    return AadhaarAdapterResult(
        document=_document("aadhaar-1", "Aadhaar", "aadhaar"),
        evidence=evidence,
    )


def _run_chain(
    passport_evidence: list[Evidence],
    aadhaar_evidence: list[Evidence],
    *,
    visa_evidence: list[Evidence] | None = None,
):
    case = run_case(
        "passport.png",
        "visa.png",
        passport_runner=lambda _: _passport(passport_evidence),
        visa_runner=lambda _: _visa(visa_evidence),
        aadhaar_image_path="aadhaar.png",
        aadhaar_runner=lambda _: _aadhaar(aadhaar_evidence),
    )
    assessment = aggregate_risk(case.evidence, case.contradictions)
    return case, assessment, make_decision(assessment)


class P6ReasoningChainTests(unittest.TestCase):
    def test_matching_passport_aadhaar_case_remains_clear(self) -> None:
        case, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-name",
                    "passport-1",
                    "name",
                    "ARUN KUMAR",
                    "passport.visual_fields",
                ),
                _evidence(
                    "p-dob",
                    "passport-1",
                    "dob",
                    "2005-04-12",
                    "passport.visual_fields",
                ),
            ],
            [
                _evidence(
                    "a-name",
                    "aadhaar-1",
                    "printed.name",
                    "ARUN KUMAR",
                    "aadhaar.printed",
                ),
                _evidence(
                    "a-dob",
                    "aadhaar-1",
                    "printed.dob",
                    "2005-04-12",
                    "aadhaar.printed",
                ),
            ],
        )

        self.assertEqual(case.contradictions, [])
        self.assertEqual(assessment.status, ScreeningStatus.CLEAR)
        self.assertFalse(assessment.review_required)
        self.assertEqual(decision.status, ScreeningStatus.CLEAR)
        self.assertFalse(decision.review_required)

    def test_medium_name_contradiction_propagates_to_review(self) -> None:
        case, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-name",
                    "passport-1",
                    "name",
                    "ARUN KUMAR",
                    "passport.visual_fields",
                )
            ],
            [
                _evidence(
                    "a-name",
                    "aadhaar-1",
                    "printed.name",
                    "ARUN KUMER",
                    "aadhaar.printed",
                )
            ],
        )

        self.assertEqual(len(case.contradictions), 1)
        contradiction = case.contradictions[0]
        self.assertEqual(contradiction.severity, "MEDIUM")
        self.assertEqual(assessment.status, ScreeningStatus.REVIEW)
        self.assertTrue(assessment.review_required)
        self.assertEqual(decision.status, ScreeningStatus.REVIEW)
        self.assertTrue(decision.review_required)
        self.assertEqual(
            decision.supporting_contradiction_ids,
            [contradiction.contradiction_id],
        )

    def test_high_dob_contradiction_propagates_to_high_review(self) -> None:
        case, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-dob",
                    "passport-1",
                    "dob",
                    "2005-04-12",
                    "passport.visual_fields",
                )
            ],
            [
                _evidence(
                    "a-dob",
                    "aadhaar-1",
                    "printed.dob",
                    "2005-04-13",
                    "aadhaar.printed",
                )
            ],
        )

        self.assertEqual(len(case.contradictions), 1)
        self.assertEqual(case.contradictions[0].severity, "HIGH")
        self.assertEqual(assessment.status, ScreeningStatus.HIGH_REVIEW)
        self.assertTrue(assessment.review_required)
        self.assertEqual(decision.status, ScreeningStatus.HIGH_REVIEW)
        self.assertTrue(decision.review_required)

    def test_poor_quality_is_inconclusive_not_fraud_evidence(self) -> None:
        _, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-quality",
                    "passport-1",
                    "image_quality",
                    "POOR",
                    "passport.quality",
                    quality=0.2,
                )
            ],
            [],
        )

        self.assertEqual(assessment.status, ScreeningStatus.INCONCLUSIVE)
        self.assertTrue(assessment.review_required)
        self.assertEqual(decision.status, ScreeningStatus.INCONCLUSIVE)
        text = " ".join(assessment.reasons).casefold()
        self.assertIn("poor quality", text)
        self.assertNotIn("fraud", text)
        self.assertNotIn("fake", text)

    def test_unavailable_and_none_confidence_do_not_create_new_negative_signal(self) -> None:
        case, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-name",
                    "passport-1",
                    "name",
                    "ARUN KUMAR",
                    "passport.visual_fields",
                )
            ],
            [
                _evidence(
                    "a-qr-status",
                    "aadhaar-1",
                    "qr.status",
                    "NOT_CHECKED",
                    "aadhaar.qr",
                ),
                _evidence(
                    "a-name",
                    "aadhaar-1",
                    "printed.name",
                    "ARUN KUMER",
                    "aadhaar.printed",
                ),
            ],
        )

        self.assertEqual(len(case.contradictions), 1)
        self.assertIsNone(case.contradictions[0].confidence)
        self.assertEqual(assessment.status, ScreeningStatus.REVIEW)
        self.assertEqual(decision.status, ScreeningStatus.REVIEW)
        self.assertNotIn("NOT_CHECKED", " ".join(assessment.reasons))

    def test_three_document_contradictions_survive_without_duplicates(self) -> None:
        case, assessment, decision = _run_chain(
            [
                _evidence(
                    "p-number",
                    "passport-1",
                    "passport_number",
                    "A12345678",
                    "passport.visual_fields",
                ),
                _evidence(
                    "p-name",
                    "passport-1",
                    "name",
                    "ARUN KUMAR",
                    "passport.visual_fields",
                ),
            ],
            [
                _evidence(
                    "a-name",
                    "aadhaar-1",
                    "printed.name",
                    "ARUN KUMER",
                    "aadhaar.printed",
                )
            ],
            visa_evidence=[
                _evidence(
                    "v-number",
                    "visa-1",
                    "passport_no",
                    "B98765432",
                    "visa.ocr",
                )
            ],
        )

        self.assertEqual(len(case.contradictions), 2)
        self.assertEqual(
            {item.severity for item in case.contradictions},
            {"HIGH", "MEDIUM"},
        )
        contradiction_ids = [
            item.contradiction_id for item in case.contradictions
        ]
        self.assertEqual(len(contradiction_ids), len(set(contradiction_ids)))
        self.assertEqual(
            set(assessment.supporting_contradiction_ids),
            set(contradiction_ids),
        )
        self.assertEqual(
            set(decision.supporting_contradiction_ids),
            set(contradiction_ids),
        )
        self.assertEqual(assessment.status, ScreeningStatus.HIGH_REVIEW)
        self.assertTrue(decision.review_required)


if __name__ == "__main__":
    unittest.main()
