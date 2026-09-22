"""Reviewer-facing interpretation of a DAKSH risk assessment."""

from pydantic import BaseModel, Field

from app.schemas import ScreeningStatus
from app.services.risk_aggregator import RiskAssessment


class DecisionResult(BaseModel):
    """Final review-priority decision without fraud classification."""

    status: ScreeningStatus
    review_required: bool
    headline: str
    reasons: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    supporting_contradiction_ids: list[str] = Field(default_factory=list)


_HEADLINES = {
    ScreeningStatus.CLEAR: "No significant inconsistency detected",
    ScreeningStatus.LOW_CONCERN: "Minor issue requires attention",
    ScreeningStatus.REVIEW: "Cross-document inconsistency requires review",
    ScreeningStatus.HIGH_REVIEW: (
        "High-priority inconsistency requires manual verification"
    ),
    ScreeningStatus.INCONCLUSIVE: (
        "Assessment inconclusive because document quality is insufficient"
    ),
}

_FALLBACK_ACTIONS = {
    ScreeningStatus.CLEAR: (
        "No additional action is indicated by the available evidence."
    ),
    ScreeningStatus.LOW_CONCERN: (
        "Review the low-priority signal if other case context warrants it."
    ),
    ScreeningStatus.REVIEW: (
        "Review the available evidence and verify the affected fields manually."
    ),
    ScreeningStatus.HIGH_REVIEW: (
        "Perform manual verification of the high-priority finding."
    ),
    ScreeningStatus.INCONCLUSIVE: (
        "Obtain a clearer document image and rerun the affected checks."
    ),
}


def make_decision(assessment: RiskAssessment) -> DecisionResult:
    """Convert an existing risk assessment without adding new findings."""

    next_actions = list(assessment.next_actions)
    if not next_actions:
        next_actions = [_FALLBACK_ACTIONS[assessment.status]]

    return DecisionResult(
        status=assessment.status,
        review_required=assessment.review_required,
        headline=_HEADLINES[assessment.status],
        reasons=list(assessment.reasons),
        next_actions=next_actions,
        supporting_evidence_ids=list(assessment.supporting_evidence_ids),
        supporting_contradiction_ids=list(
            assessment.supporting_contradiction_ids
        ),
    )
