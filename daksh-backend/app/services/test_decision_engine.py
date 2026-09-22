import unittest

from app.schemas import ScreeningStatus
from app.services.decision_engine import DecisionResult, make_decision
from app.services.risk_aggregator import RiskAssessment


def assessment(status: ScreeningStatus) -> RiskAssessment:
    return RiskAssessment(
        status=status,
        review_required=status is not ScreeningStatus.CLEAR,
        reasons=["Reason tied to upstream assessment."],
        next_actions=["Review the available evidence."],
        supporting_evidence_ids=["e-1"],
        supporting_contradiction_ids=["c-1"],
    )


class DecisionEngineTests(unittest.TestCase):
    def test_clear_assessment_remains_clear(self) -> None:
        result = make_decision(assessment(ScreeningStatus.CLEAR))
        self.assertEqual(result.status, ScreeningStatus.CLEAR)
        self.assertFalse(result.review_required)

    def test_low_concern_remains_low_concern(self) -> None:
        result = make_decision(assessment(ScreeningStatus.LOW_CONCERN))
        self.assertEqual(result.status, ScreeningStatus.LOW_CONCERN)
        self.assertTrue(result.review_required)

    def test_review_remains_review(self) -> None:
        result = make_decision(assessment(ScreeningStatus.REVIEW))
        self.assertEqual(result.status, ScreeningStatus.REVIEW)
        self.assertTrue(result.review_required)

    def test_high_review_remains_high_review(self) -> None:
        result = make_decision(assessment(ScreeningStatus.HIGH_REVIEW))
        self.assertEqual(result.status, ScreeningStatus.HIGH_REVIEW)
        self.assertTrue(result.review_required)

    def test_inconclusive_remains_inconclusive(self) -> None:
        result = make_decision(assessment(ScreeningStatus.INCONCLUSIVE))
        self.assertEqual(result.status, ScreeningStatus.INCONCLUSIVE)
        self.assertTrue(result.review_required)

    def test_reasons_are_preserved(self) -> None:
        source = assessment(ScreeningStatus.REVIEW)
        result = make_decision(source)
        self.assertEqual(result.reasons, source.reasons)

    def test_supporting_ids_are_preserved(self) -> None:
        source = assessment(ScreeningStatus.HIGH_REVIEW)
        result = make_decision(source)
        self.assertEqual(result.supporting_evidence_ids, ["e-1"])
        self.assertEqual(result.supporting_contradiction_ids, ["c-1"])

    def test_next_actions_are_present_and_factual(self) -> None:
        result = make_decision(assessment(ScreeningStatus.REVIEW))
        self.assertTrue(result.next_actions)
        text = " ".join(result.next_actions).casefold()
        self.assertNotIn("government database", text)
        self.assertNotIn("probability", text)

    def test_empty_upstream_actions_get_status_fallback(self) -> None:
        source = RiskAssessment(
            status=ScreeningStatus.INCONCLUSIVE,
            review_required=True,
        )
        result = make_decision(source)
        self.assertEqual(
            result.next_actions,
            ["Obtain a clearer document image and rerun the affected checks."],
        )

    def test_decision_contains_no_prohibited_classification(self) -> None:
        for status in ScreeningStatus:
            result = make_decision(assessment(status))
            text = (
                result.headline
                + " "
                + " ".join(result.reasons)
                + " "
                + " ".join(result.next_actions)
            ).casefold()
            for prohibited in (
                "fake",
                "genuine",
                "fraud",
                "authentic",
                "probability",
                "%",
            ):
                self.assertNotIn(prohibited, text)
            self.assertIsInstance(result, DecisionResult)


if __name__ == "__main__":
    unittest.main()
