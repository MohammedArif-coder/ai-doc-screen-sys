"""Deterministic cross-document contradiction detection."""

from datetime import datetime
import re
from typing import Any

from app.schemas import Contradiction, Evidence, EvidenceType


FIELD_MAPPINGS = {
    "passport_number": "passport_no",
    "name": "applicant_name",
    "nationality": "nationality",
    "expiry_date": "expiry_date",
    "issue_date": "issue_date",
}

HIGH_SEVERITY_FIELDS = {"passport_number"}

# These mappings only compare values when both corresponding evidence items
# actually exist. Aadhaar printed and QR values intentionally remain separate.
AADHAAR_MAPPINGS = (
    ("passport", "name", "aadhaar", "printed.name", "MEDIUM"),
    ("passport", "name", "aadhaar", "qr.name", "MEDIUM"),
    ("passport", "dob", "aadhaar", "printed.dob", "HIGH"),
    ("passport", "dob", "aadhaar", "qr.dob", "HIGH"),
    ("passport", "date_of_birth", "aadhaar", "printed.dob", "HIGH"),
    ("passport", "date_of_birth", "aadhaar", "qr.dob", "HIGH"),
    ("passport", "sex", "aadhaar", "printed.gender", "MEDIUM"),
    ("passport", "sex", "aadhaar", "qr.gender", "MEDIUM"),
)

DL_MAPPINGS = (
    ("passport", "name", "driving_licence", "name", "MEDIUM"),
    ("passport", "dob", "driving_licence", "dob", "HIGH"),
    ("aadhaar", "printed.name", "driving_licence", "name", "MEDIUM"),
    ("aadhaar", "printed.dob", "driving_licence", "dob", "HIGH"),
)

PAN_MAPPINGS = (
    ("passport", "name", "pan", "name", "MEDIUM"),
    ("passport", "dob", "pan", "dob", "HIGH"),
    ("aadhaar", "printed.name", "pan", "name", "MEDIUM"),
    ("aadhaar", "printed.dob", "pan", "dob", "HIGH"),
    ("driving_licence", "name", "pan", "name", "MEDIUM"),
    ("driving_licence", "dob", "pan", "dob", "HIGH"),
)


def _source_module(evidence: Evidence) -> str:
    return evidence.source.split(".", 1)[0].lower()


def _normalize_text(value: Any, *, field: str) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None
    text = re.sub(r"\s+", " ", text).casefold()

    if field in {"name", "passport_number"}:
        text = re.sub(r"[,\-]+", " ", text)
        if field == "passport_number":
            text = text.replace(" ", "")
        else:
            text = re.sub(r"\s+", " ", text).strip()

    return text


def _normalize_date(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text:
        return None

    patterns = (
        ("%Y-%m-%d", r"\d{4}-\d{2}-\d{2}"),
        ("%Y/%m/%d", r"\d{4}/\d{2}/\d{2}"),
        ("%d/%m/%Y", r"\d{2}/\d{2}/\d{4}"),
        ("%d-%m-%Y", r"\d{2}-\d{2}-\d{4}"),
    )
    for format_string, pattern in patterns:
        if re.fullmatch(pattern, text):
            try:
                return datetime.strptime(text, format_string).date().isoformat()
            except ValueError:
                return None
    return None


def _normalized_value(value: Any, field: str) -> str | None:
    if field in {"expiry_date", "issue_date", "dob", "date_of_birth"}:
        return _normalize_date(value)
    return _normalize_text(value, field=field)


def _candidate_score(evidence: Evidence, expected_field: str) -> tuple[int, int, int]:
    direct_source = (
        (expected_field == "passport_number" and evidence.source == "passport.visual_fields")
        or (expected_field == "passport_no" and evidence.source == "visa.ocr")
        or (expected_field == "name" and evidence.source in {"passport.visual_fields", "visa.ocr"})
        or evidence.source.endswith(".visual_fields")
        or evidence.source.endswith(".ocr")
    )
    return (
        int(evidence.evidence_type == EvidenceType.OBSERVATION),
        int(evidence.confidence is not None),
        int(direct_source),
    )


def _select_evidence(
    evidence: list[Evidence],
    *,
    module: str,
    field: str,
) -> Evidence | None:
    candidates = [
        item
        for item in evidence
        if _source_module(item) == module
        and item.field == field
        and _normalized_value(item.value, field) is not None
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda item: _candidate_score(item, field))


def _comparison_confidence(
    evidence_a: Evidence,
    evidence_b: Evidence,
) -> float | None:
    if evidence_a.confidence is None or evidence_b.confidence is None:
        return None
    return min(evidence_a.confidence, evidence_b.confidence)


def _make_contradiction(**values: Any) -> Contradiction:
    confidence = values.get("confidence")
    if confidence is not None:
        return Contradiction(**values)

    # The current schema predates nullable contradiction confidence. Preserve
    # the truthful None value without changing that shared schema in this task.
    return Contradiction.model_construct(**values)


def detect_contradictions(evidence: list[Evidence]) -> list[Contradiction]:
    """Return deterministic mismatches across available document evidence."""

    contradictions: list[Contradiction] = []
    compared_pairs: set[tuple[str, str, str, str]] = set()

    for passport_field, visa_field in FIELD_MAPPINGS.items():
        passport_item = _select_evidence(
            evidence,
            module="passport",
            field=passport_field,
        )
        visa_item = _select_evidence(
            evidence,
            module="visa",
            field=visa_field,
        )
        if passport_item is None or visa_item is None:
            continue
        compared_pairs.add(
            (passport_item.evidence_id, visa_item.evidence_id, passport_field, visa_field)
        )

        normalized_passport = _normalized_value(
            passport_item.value,
            passport_field,
        )
        normalized_visa = _normalized_value(
            visa_item.value,
            passport_field,
        )
        if normalized_passport is None or normalized_visa is None:
            continue
        if normalized_passport == normalized_visa:
            continue

        confidence = _comparison_confidence(passport_item, visa_item)
        confidence_note = (
            " Confidence was unavailable for one or both source evidence items."
            if confidence is None
            else ""
        )
        severity = "HIGH" if passport_field in HIGH_SEVERITY_FIELDS else "MEDIUM"

        contradictions.append(
            _make_contradiction(
                contradiction_id=(
                    f"{passport_item.document_id}:{visa_item.document_id}:"
                    f"{passport_field}"
                ),
                field=passport_field,
                document_a=passport_item.document_id,
                document_b=visa_item.document_id,
                value_a=passport_item.value,
                value_b=visa_item.value,
                normalized_value_a=normalized_passport,
                normalized_value_b=normalized_visa,
                comparison="MISMATCH",
                confidence=confidence,
                severity=severity,
                explanation=(
                    f"The {passport_field.replace('_', ' ')} differs between "
                    f"the Passport evidence ({passport_item.evidence_id}, "
                    f"source {passport_item.source}) and Visa evidence "
                    f"({visa_item.evidence_id}, source {visa_item.source})."
                    f"{confidence_note}"
                ),
            )
        )

    for module_a, field_a, module_b, field_b, severity in (
        AADHAAR_MAPPINGS + DL_MAPPINGS + PAN_MAPPINGS
    ):
        item_a = _select_evidence(evidence, module=module_a, field=field_a)
        item_b = _select_evidence(evidence, module=module_b, field=field_b)
        if item_a is None or item_b is None:
            continue

        pair = (item_a.evidence_id, item_b.evidence_id, field_a, field_b)
        if pair in compared_pairs:
            continue
        compared_pairs.add(pair)

        normalized_a = _normalized_value(item_a.value, field_a)
        normalized_b = _normalized_value(item_b.value, field_a)
        if normalized_a is None or normalized_b is None:
            continue
        if normalized_a == normalized_b:
            continue

        confidence = _comparison_confidence(item_a, item_b)
        confidence_note = (
            " Confidence was unavailable for one or both source evidence items."
            if confidence is None
            else ""
        )
        contradictions.append(
            _make_contradiction(
                contradiction_id=(
                    f"{item_a.document_id}:{item_b.document_id}:"
                    f"{field_a}:{field_b}"
                ),
                field=field_a,
                document_a=item_a.document_id,
                document_b=item_b.document_id,
                value_a=item_a.value,
                value_b=item_b.value,
                normalized_value_a=normalized_a,
                normalized_value_b=normalized_b,
                comparison="MISMATCH",
                confidence=confidence,
                severity=severity,
                explanation=(
                    f"The {field_a.replace('_', ' ')} differs between "
                    f"evidence {item_a.evidence_id} (source {item_a.source}) "
                    f"and evidence {item_b.evidence_id} "
                    f"(source {item_b.source}).{confidence_note}"
                ),
            )
        )

    return contradictions
