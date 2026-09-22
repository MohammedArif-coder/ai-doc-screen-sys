"""Deterministic review-priority aggregation for P6 case outputs."""

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from app.schemas import Contradiction, Evidence, ScreeningStatus


class RiskAssessment(BaseModel):
    """Explainable review priority; not a fraud or authenticity score."""

    status: ScreeningStatus
    review_required: bool
    reasons: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    supporting_contradiction_ids: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class _Signal:
    priority: int
    reason: str
    evidence_id: str | None = None
    contradiction_id: str | None = None
    inconclusive: bool = False
    quality_only: bool = False


_SEVERITY_PRIORITY = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
_UNAVAILABLE_WORDS = {"unavailable", "not_available", "not available", "missing"}


def _severity(value: str | None) -> int:
    return _SEVERITY_PRIORITY.get(value.upper(), 0) if isinstance(value, str) else 0


def _is_unavailable(evidence: Evidence) -> bool:
    if evidence.value is None:
        return True
    if isinstance(evidence.value, str):
        return evidence.value.strip().casefold() in _UNAVAILABLE_WORDS
    return False


def _signal_key(evidence: Evidence) -> tuple[Any, ...]:
    field = evidence.field.casefold().strip()
    source = evidence.source.casefold().strip()
    value = repr(evidence.value)
    if "tamper" in field or "tamper" in source:
        return ("tamper", value)
    return (source, field, value)


def _select_evidence_signals(evidence: list[Evidence]) -> list[Evidence]:
    selected: dict[tuple[Any, ...], Evidence] = {}
    for item in evidence:
        if _is_unavailable(item):
            continue
        if _severity(item.severity) == 0 and item.quality is None:
            continue
        key = _signal_key(item)
        current = selected.get(key)
        if current is None:
            selected[key] = item
            continue
        current_rank = (
            _severity(current.severity),
            int(current.confidence is not None),
            current.confidence or -1.0,
        )
        item_rank = (
            _severity(item.severity),
            int(item.confidence is not None),
            item.confidence or -1.0,
        )
        if item_rank > current_rank:
            selected[key] = item
    return list(selected.values())


def _contradiction_signal(item: Contradiction) -> _Signal | None:
    priority = _severity(item.severity)
    if priority == 0:
        return None
    return _Signal(
        priority=priority,
        contradiction_id=item.contradiction_id,
        reason=(
            f"Contradiction {item.contradiction_id} is {item.severity} severity "
            f"for {item.field}: {item.explanation}"
        ),
    )


def _evidence_signals(evidence: list[Evidence]) -> list[_Signal]:
    signals: list[_Signal] = []
    for item in _select_evidence_signals(evidence):
        severity = _severity(item.severity)
        if severity:
            confidence_note = (
                " Confidence was unavailable."
                if item.confidence is None
                else (
                    " Confidence was low, so certainty is limited."
                    if item.confidence < 0.5
                    else ""
                )
            )
            signals.append(
                _Signal(
                    priority=severity,
                    evidence_id=item.evidence_id,
                    inconclusive=item.confidence is None or item.confidence < 0.5,
                    reason=(
                        f"Evidence {item.evidence_id} reports {item.severity} "
                        f"severity for {item.field}.{confidence_note}"
                    ),
                )
            )
        if item.quality is not None and item.quality < 0.5:
            signals.append(
                _Signal(
                    priority=1,
                    evidence_id=item.evidence_id,
                    inconclusive=True,
                    quality_only=True,
                    reason=(
                        f"Evidence {item.evidence_id} indicates poor quality for "
                        f"{item.field}; the check may require better input."
                    ),
                )
            )
    return signals


def aggregate_risk(
    evidence: list[Evidence],
    contradictions: list[Contradiction],
) -> RiskAssessment:
    """Aggregate findings into a transparent review-priority assessment."""

    signals = [
        signal
        for contradiction in contradictions
        if (signal := _contradiction_signal(contradiction)) is not None
    ]
    signals.extend(_evidence_signals(evidence))

    highest_priority = max((signal.priority for signal in signals), default=0)
    has_inconclusive = any(signal.inconclusive for signal in signals)

    if highest_priority >= 3:
        status = ScreeningStatus.HIGH_REVIEW
    elif highest_priority == 2:
        status = ScreeningStatus.REVIEW
    elif highest_priority == 1 and not any(
        signal.quality_only for signal in signals
    ):
        status = ScreeningStatus.LOW_CONCERN
    elif has_inconclusive:
        status = ScreeningStatus.INCONCLUSIVE
    else:
        status = ScreeningStatus.CLEAR

    reasons = [signal.reason for signal in signals]
    evidence_ids = list(dict.fromkeys(
        signal.evidence_id for signal in signals if signal.evidence_id is not None
    ))
    contradiction_ids = list(dict.fromkeys(
        signal.contradiction_id
        for signal in signals
        if signal.contradiction_id is not None
    ))

    if status is ScreeningStatus.HIGH_REVIEW:
        next_actions = [
            "Perform manual review of the high-priority contradiction or finding.",
            "Verify the affected fields against the original documents.",
        ]
    elif status is ScreeningStatus.REVIEW:
        next_actions = [
            "Perform manual review of the reported contradiction or finding.",
            "Verify affected fields and source evidence.",
        ]
    elif status is ScreeningStatus.LOW_CONCERN:
        next_actions = ["Review the low-priority signal if other case context warrants it."]
    elif status is ScreeningStatus.INCONCLUSIVE:
        next_actions = ["Obtain a clearer document image or rerun unavailable checks."]
    else:
        next_actions = ["No additional action is indicated by the available signals."]

    return RiskAssessment(
        status=status,
        review_required=status is not ScreeningStatus.CLEAR,
        reasons=reasons,
        next_actions=next_actions,
        supporting_evidence_ids=evidence_ids,
        supporting_contradiction_ids=contradiction_ids,
    )
