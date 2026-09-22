"""Adapter for the independently running Passport screening service."""

from dataclasses import dataclass, field
import mimetypes
from pathlib import Path
from typing import Any

import requests

from app.schemas import Document, Evidence, EvidenceType


PASSPORT_SCREEN_URL = "http://127.0.0.1:8000/api/passport/screen"


@dataclass
class PassportAdapterResult:
    """DAKSH representation of one Passport screening request."""

    document: Document
    evidence: list[Evidence] = field(default_factory=list)
    raw_response: dict[str, Any] | None = None
    error: str | None = None
    unmapped_fields: list[str] = field(default_factory=list)


def _document_id(image_path: Path) -> str:
    return image_path.name


def _has_meaningful_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (dict, list, tuple, set)):
        return bool(value)
    return True


def _evidence_from_item(
    *,
    evidence_id: str,
    document_id: str,
    evidence_type: EvidenceType,
    field_name: str,
    value: Any,
    source: str,
    normalized_value: Any | None = None,
    description: str | None = None,
) -> Evidence | None:
    """Create evidence while preserving unavailable confidence as None."""

    if not _has_meaningful_value(value):
        return None

    return Evidence(
        evidence_id=evidence_id,
        document_id=document_id,
        evidence_type=evidence_type,
        field=field_name,
        value=value,
        normalized_value=normalized_value,
        confidence=None,
        source=source,
        description=description,
    )


def _add_nested_evidence(
    *,
    evidence: list[Evidence],
    document_id: str,
    evidence_type: EvidenceType,
    field_prefix: str,
    value: Any,
    source: str,
) -> None:
    if isinstance(value, dict):
        for key, nested_value in value.items():
            _add_nested_evidence(
                evidence=evidence,
                document_id=document_id,
                evidence_type=evidence_type,
                field_prefix=f"{field_prefix}.{key}",
                value=nested_value,
                source=source,
            )
        return

    if isinstance(value, list):
        for index, nested_value in enumerate(value):
            _add_nested_evidence(
                evidence=evidence,
                document_id=document_id,
                evidence_type=evidence_type,
                field_prefix=f"{field_prefix}[{index}]",
                value=nested_value,
                source=source,
            )
        return

    item = _evidence_from_item(
        evidence_id=f"{document_id}:{source}:{field_prefix}",
        document_id=document_id,
        evidence_type=evidence_type,
        field_name=field_prefix,
        value=value,
        source=source,
    )
    if item is not None:
        evidence.append(item)


def adapt_passport_response(
    response: dict[str, Any],
    *,
    document_id: str,
) -> PassportAdapterResult:
    """Convert a real Passport response without adding module-derived values."""

    if not isinstance(response, dict):
        raise ValueError("Passport response must be a JSON object.")

    evidence: list[Evidence] = []
    unmapped_fields: list[str] = []

    visual_fields = response.get("visual_fields")
    if isinstance(visual_fields, dict):
        for field_name, value in visual_fields.items():
            item = _evidence_from_item(
                evidence_id=f"{document_id}:visual_fields:{field_name}",
                document_id=document_id,
                evidence_type=EvidenceType.OBSERVATION,
                field_name=field_name,
                value=value,
                source="passport.visual_fields",
            )
            if item is not None:
                evidence.append(item)

    mrz = response.get("mrz")
    if isinstance(mrz, dict):
        for field_name in ("line1", "line2"):
            item = _evidence_from_item(
                evidence_id=f"{document_id}:mrz:{field_name}",
                document_id=document_id,
                evidence_type=EvidenceType.OBSERVATION,
                field_name=field_name,
                value=mrz.get(field_name),
                source="passport.mrz",
            )
            if item is not None:
                evidence.append(item)

        parsed = mrz.get("parsed")
        if isinstance(parsed, dict):
            for field_name, value in parsed.items():
                item = _evidence_from_item(
                    evidence_id=f"{document_id}:mrz.parsed:{field_name}",
                    document_id=document_id,
                    evidence_type=EvidenceType.OBSERVATION,
                    field_name=field_name,
                    value=value,
                    source="passport.mrz.parsed",
                )
                if item is not None:
                    evidence.append(item)

    mrz_validation = response.get("mrz_validation")
    if isinstance(mrz_validation, dict):
        for field_name in ("line1_length", "line2_length"):
            item = _evidence_from_item(
                evidence_id=f"{document_id}:mrz_validation:{field_name}",
                document_id=document_id,
                evidence_type=EvidenceType.DERIVED,
                field_name=field_name,
                value=mrz_validation.get(field_name),
                source="passport.mrz_validation",
            )
            if item is not None:
                evidence.append(item)

        checks = mrz_validation.get("checks")
        if isinstance(checks, dict):
            for field_name, value in checks.items():
                item = _evidence_from_item(
                    evidence_id=f"{document_id}:mrz_validation:checks:{field_name}",
                    document_id=document_id,
                    evidence_type=EvidenceType.DERIVED,
                    field_name=field_name,
                    value=value,
                    source="passport.mrz_validation",
                )
                if item is not None:
                    evidence.append(item)

    consistency = response.get("consistency")
    if isinstance(consistency, list):
        for index, comparison in enumerate(consistency):
            if not isinstance(comparison, dict):
                field_name = str(index)
            else:
                field_name = str(comparison.get("field") or index)
            item = _evidence_from_item(
                evidence_id=f"{document_id}:consistency:{index}",
                document_id=document_id,
                evidence_type=EvidenceType.DERIVED,
                field_name=field_name,
                value=comparison,
                source="passport.consistency",
            )
            if item is not None:
                evidence.append(item)

    forensics = response.get("forensics")
    if isinstance(forensics, dict):
        for category, observations in forensics.items():
            _add_nested_evidence(
                evidence=evidence,
                document_id=document_id,
                evidence_type=EvidenceType.OBSERVATION,
                field_prefix=category,
                value=observations,
                source=f"passport.forensics.{category}",
            )

    summary = response.get("summary")
    if isinstance(summary, dict):
        for field_name, value in summary.items():
            item = _evidence_from_item(
                evidence_id=f"{document_id}:summary:{field_name}",
                document_id=document_id,
                evidence_type=EvidenceType.DERIVED,
                field_name=field_name,
                value=value,
                source="passport.summary",
            )
            if item is not None:
                evidence.append(item)

    status = response.get("status")
    processing_status = status if isinstance(status, str) else "malformed_response"
    item = _evidence_from_item(
        evidence_id=f"{document_id}:status",
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field_name="status",
        value=status,
        source="passport.status",
    )
    if item is not None:
        evidence.append(item)

    reason = response.get("reason")
    item = _evidence_from_item(
        evidence_id=f"{document_id}:reason",
        document_id=document_id,
        evidence_type=EvidenceType.OBSERVATION,
        field_name="reason",
        value=reason,
        source="passport.processing",
    )
    if item is not None:
        evidence.append(item)

    handled_fields = {
        "visual_fields",
        "mrz",
        "mrz_validation",
        "consistency",
        "forensics",
        "summary",
        "status",
        "reason",
    }
    unmapped_fields.extend(
        f"response.{key}" for key in response if key not in handled_fields
    )

    return PassportAdapterResult(
        document=Document(
            document_id=document_id,
            document_type="Passport",
            source_module="passport",
            processing_status=processing_status,
        ),
        evidence=evidence,
        raw_response=response,
        unmapped_fields=unmapped_fields,
    )


def screen_passport_file(
    image_path: str | Path,
    *,
    timeout: float = 300.0,
    endpoint: str = PASSPORT_SCREEN_URL,
) -> PassportAdapterResult:
    """Submit a local image to Passport and return the DAKSH representation."""

    path = Path(image_path)
    document_id = _document_id(path)

    if not path.is_file():
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="error",
            ),
            error=f"Passport image file not found: {path}",
        )

    content_type = mimetypes.guess_type(path.name)[0]
    if content_type not in {"image/jpeg", "image/png"}:
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="invalid_input",
            ),
            error="Passport image must be a JPG or PNG file.",
        )

    try:
        with path.open("rb") as image_file:
            response = requests.post(
                endpoint,
                files={"file": (path.name, image_file, content_type)},
                timeout=timeout,
            )
    except requests.RequestException as exc:
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="service_unavailable",
            ),
            error=f"Passport service unavailable: {exc}",
        )

    if not response.ok:
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="http_error",
            ),
            error=f"Passport service returned HTTP {response.status_code}: {response.text}",
        )

    try:
        payload = response.json()
    except ValueError as exc:
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="malformed_response",
            ),
            error=f"Passport service returned invalid JSON: {exc}",
        )

    try:
        return adapt_passport_response(payload, document_id=document_id)
    except (TypeError, ValueError) as exc:
        return PassportAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Passport",
                source_module="passport",
                processing_status="malformed_response",
            ),
            raw_response=payload if isinstance(payload, dict) else None,
            error=f"Malformed Passport response: {exc}",
        )
