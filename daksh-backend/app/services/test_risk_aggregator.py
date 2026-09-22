import unittest

from app.schemas import Contradiction, Evidence, EvidenceType, ScreeningStatus
from app.services.risk_aggregator import aggregate_risk


def evidence(
    evidence_id: str,
    *,
    field: str = "check",
    value: object = "finding",
    severity: str | None = None,
    confidence: float | None = None,
    quality: float | None = None,
    source: str = "visa.test",
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        document_id="doc-1",
        evidence_type=EvidenceType.OBSERVATION,
        field=field,
        value=value,
        severity=severity,
        confidence=confidence,
        quality=quality,
        source=source,
    )


def contradiction(
    contradiction_id: str,
    severity: str,
) -> Contradiction:
    return Contradiction(
        contradiction_id=contradiction_id,
        field="passport_number",
        document_a="passport-1",
        document_b="visa-1",
        value_a="A123",
        value_b="B456",
        comparison="MISMATCH",
        severity=severity,
        explanation="The values differ.",
    )


class RiskAggregatorTests(unittest.TestCase):
    def test_no_concerning_evidence_is_clear(self) -> None:
        result = aggregate_risk([], [])
        self.assertEqual(result.status, ScreeningStatus.CLEAR)
        self.assertFalse(result.review_required)

    def test_low_contradiction_increases_priority(self) -> None:
        result = aggregate_risk([], [contradiction("c-low", "LOW")])
        self.assertEqual(result.status, ScreeningStatus.LOW_CONCERN)
        self.assertTrue(result.review_required)

    def test_medium_contradiction_requires_review(self) -> None:
        result = aggregate_risk([], [contradiction("c-medium", "MEDIUM")])
        self.assertEqual(result.status, ScreeningStatus.REVIEW)

    def test_high_contradiction_requires_high_review(self) -> None:
        result = aggregate_risk([], [contradiction("c-high", "HIGH")])
        self.assertEqual(result.status, ScreeningStatus.HIGH_REVIEW)
        self.assertNotIn("FAKE", " ".join(result.reasons))

    def test_low_confidence_finding_is_not_fake(self) -> None:
        result = aggregate_risk(
            [evidence("e-low", severity="MEDIUM", confidence=0.2)],
            [],
        )
        self.assertEqual(result.status, ScreeningStatus.REVIEW)
        self.assertIn("certainty is limited", result.reasons[0])
        self.assertNotIn("FAKE", " ".join(result.reasons))

    def test_unavailable_confidence_is_preserved_safely(self) -> None:
        result = aggregate_risk(
            [evidence("e-none", severity="LOW", confidence=None)],
            [],
        )
        self.assertEqual(result.status, ScreeningStatus.LOW_CONCERN)
        self.assertIn("unavailable", result.reasons[0])

    def test_poor_quality_is_not_fraud_evidence(self) -> None:
        result = aggregate_risk(
            [evidence("e-quality", field="image_quality", quality=0.2)],
            [],
        )
        self.assertEqual(result.status, ScreeningStatus.INCONCLUSIVE)
        self.assertIn("poor quality", result.reasons[0])
        self.assertNotIn("fraud", " ".join(result.reasons).casefold())

    def test_unavailable_check_does_not_increase_priority(self) -> None:
        result = aggregate_risk(
            [evidence("e-missing", field="biometric", value="unavailable")],
            [],
        )
        self.assertEqual(result.status, ScreeningStatus.CLEAR)
        self.assertEqual(result.supporting_evidence_ids, [])

    def test_correlated_tamper_signals_are_not_double_counted(self) -> None:
        items = [
            evidence(
                "e-tamper-observation",
                field="signal_detected",
                value=True,
                severity="MEDIUM",
                source="visa.tamper_analysis",
            ),
            evidence(
                "e-tamper-derived",
                field="tampering_detected",
                value=True,
                severity="MEDIUM",
                source="visa.findings",
            ),
        ]
        result = aggregate_risk(items, [])
        self.assertEqual(result.status, ScreeningStatus.REVIEW)
        self.assertEqual(len(result.supporting_evidence_ids), 1)

    def test_supporting_ids_are_preserved(self) -> None:
        result = aggregate_risk(
            [evidence("e-medium", severity="MEDIUM", confidence=0.9)],
            [contradiction("c-high", "HIGH")],
        )
        self.assertEqual(result.supporting_evidence_ids, ["e-medium"])
        self.assertEqual(result.supporting_contradiction_ids, ["c-high"])


if __name__ == "__main__":
    unittest.main()
