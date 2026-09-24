"""Adapter for the independently running Aadhaar screening service."""

from dataclasses import dataclass, field
import mimetypes
from pathlib import Path
from typing import Any

import requests

from app.schemas import Document, Evidence, EvidenceType


AADHAAR_API_BASE_URL = "http://127.0.0.1:8001"
AADHAAR_SCREEN_PATH = "/api/modules/aadhaar"


@dataclass
class AadhaarAdapterResult:
    """DAKSH representation of one Aadhaar screening request."""

    document: Document
    evidence: list[Evidence] = field(default_factory=list)
    raw_response: dict[str, Any] | None = None
    error: str | None = None
    unmapped_fields: list[str] = field(default_factory=list)


def _meaningful(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (dict, list, tuple, set)):
        return bool(value)
    return True


def _confidence(value: Any) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    number = float(value)
    return number if 0.0 <= number <= 1.0 else None


def _quality(value: Any) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    number = float(value)
    if 0.0 <= number <= 1.0:
        return number
    if 0.0 <= number <= 100.0:
        return number / 100.0
    return None


def _description(confidence_basis: Any = None, note: Any = None) -> str | None:
    parts = []
    if isinstance(confidence_basis, str) and confidence_basis:
        parts.append(f"confidence_basis={confidence_basis}")
    if isinstance(note, str) and note:
        parts.append(note)
    return "; ".join(parts) or None


def _add(
    evidence: list[Evidence],
    *,
    document_id: str,
    evidence_id: str,
    evidence_type: EvidenceType,
    field: str,
    value: Any,
    source: str,
    normalized_value: Any | None = None,
    confidence: Any = None,
    quality: Any = None,
    severity: Any = None,
    region: Any = None,
    description: str | None = None,
) -> None:
    if not _meaningful(value):
        return
    evidence.append(
        Evidence(
            evidence_id=evidence_id,
            document_id=document_id,
            evidence_type=evidence_type,
            field=field,
            value=value,
            normalized_value=normalized_value,
            confidence=_confidence(confidence),
            quality=_quality(quality),
            severity=severity if isinstance(severity, str) else None,
            source=source,
            region=region if isinstance(region, dict) else None,
            description=description,
        )
    )


def _add_mapping(
    evidence: list[Evidence],
    *,
    document_id: str,
    prefix: str,
    mapping: dict[str, Any],
    source: str,
    evidence_type: EvidenceType,
    unmapped_fields: list[str],
) -> None:
    for key, value in mapping.items():
        if key in {"confidence", "confidence_basis", "status", "sources"}:
            continue
        if isinstance(value, dict):
            _add_mapping(
                evidence,
                document_id=document_id,
                prefix=f"{prefix}.{key}",
                mapping=value,
                source=source,
                evidence_type=evidence_type,
                unmapped_fields=unmapped_fields,
            )
            continue
        if isinstance(value, list):
            if not value:
                continue
            _add(
                evidence,
                document_id=document_id,
                evidence_id=f"{document_id}:{prefix}:{key}",
                evidence_type=evidence_type,
                field=f"{prefix}.{key}",
                value=value,
                source=source,
            )
            continue
        if _meaningful(value):
            _add(
                evidence,
                document_id=document_id,
                evidence_id=f"{document_id}:{prefix}:{key}",
                evidence_type=evidence_type,
                field=f"{prefix}.{key}",
                value=value,
                source=source,
                quality=_quality(value) if (prefix.startswith("quality") or key in {"score", "quality"}) else None,
            )


def adapt_aadhaar_response(
    response: dict[str, Any],
    *,
    document_id: str,
) -> AadhaarAdapterResult:
    """Translate an Aadhaar response without adding new intelligence."""

    if not isinstance(response, dict):
        raise ValueError("Aadhaar response must be a JSON object.")

    evidence: list[Evidence] = []
    unmapped_fields: list[str] = []

    fields = response.get("fields")
    if isinstance(fields, dict):
        for field_name, field_data in fields.items():
            if not isinstance(field_data, dict):
                _add(
                    evidence,
                    document_id=document_id,
                    evidence_id=f"{document_id}:printed:{field_name}",
                    evidence_type=EvidenceType.OBSERVATION,
                    field=f"printed.{field_name}",
                    value=field_data,
                    source="aadhaar.printed",
                )
                continue
            value = field_data.get("value")
            _add(
                evidence,
                document_id=document_id,
                evidence_id=f"{document_id}:printed:{field_name}",
                evidence_type=EvidenceType.OBSERVATION,
                field=f"printed.{field_name}",
                value=value,
                source="aadhaar.printed",
                normalized_value=field_data.get("normalized_value"),
                confidence=field_data.get("confidence"),
                region=(
                    {"bounding_box": field_data["bounding_box"],
                     "page": field_data.get("page")}
                    if field_data.get("bounding_box") is not None
                    else None
                ),
                description=_description(
                    field_data.get("confidence_basis"),
                    field_data.get("notes"),
                ),
            )

    observation_sections = (
        "document_identification",
        "quality",
        "orientation",
        "photo",
        "metadata",
    )
    for section in observation_sections:
        value = response.get(section)
        if isinstance(value, dict):
            _add_mapping(
                evidence,
                document_id=document_id,
                prefix=section,
                mapping=value,
                source=f"aadhaar.{section}",
                evidence_type=EvidenceType.OBSERVATION,
                unmapped_fields=unmapped_fields,
            )

    qr = response.get("qr")
    if isinstance(qr, dict):
        for key, value in qr.items():
            if key == "fields" and isinstance(value, dict):
                for qr_field, qr_value in value.items():
                    _add(
                        evidence,
                        document_id=document_id,
                        evidence_id=f"{document_id}:qr:field:{qr_field}",
                        evidence_type=EvidenceType.OBSERVATION,
                        field=f"qr.{qr_field}",
                        value=qr_value,
                        source="aadhaar.qr",
                    )
            elif key != "data_raw":
                _add(
                    evidence,
                    document_id=document_id,
                    evidence_id=f"{document_id}:qr:{key}",
                    evidence_type=EvidenceType.OBSERVATION,
                    field=f"qr.{key}",
                    value=value,
                    source="aadhaar.qr",
                )

    ekyc = response.get("offline_ekyc")
    if isinstance(ekyc, dict):
        for key, value in ekyc.items():
            if key == "fields" and isinstance(value, dict):
                _add_mapping(
                    evidence,
                    document_id=document_id,
                    prefix="offline_ekyc.fields",
                    mapping=value,
                    source="aadhaar.offline_ekyc",
                    evidence_type=EvidenceType.OBSERVATION,
                    unmapped_fields=unmapped_fields,
                )
            else:
                _add(
                    evidence,
                    document_id=document_id,
                    evidence_id=f"{document_id}:offline_ekyc:{key}",
                    evidence_type=EvidenceType.OBSERVATION,
                    field=f"offline_ekyc.{key}",
                    value=value,
                    source="aadhaar.offline_ekyc",
                )

    for section in ("number_validation", "qr_consistency", "validation"):
        value = response.get(section)
        if isinstance(value, (dict, list)):
            _add(
                evidence,
                document_id=document_id,
                evidence_id=f"{document_id}:derived:{section}",
                evidence_type=EvidenceType.DERIVED,
                field=section,
                value=value,
                source=f"aadhaar.{section}",
            )

    for section in ("contradictions", "evidence_relations"):
        value = response.get(section)
        if isinstance(value, list):
            for index, item in enumerate(value):
                item_id = (
                    item.get("contradiction_id") or item.get("relation_id")
                    if isinstance(item, dict)
                    else None
                )
                _add(
                    evidence,
                    document_id=document_id,
                    evidence_id=(
                        f"{document_id}:derived:{section}:"
                        f"{item_id or index}"
                    ),
                    evidence_type=EvidenceType.DERIVED,
                    field=f"{section}[{index}]",
                    value=item,
                    source=f"aadhaar.{section}",
                    severity=(
                        item.get("severity")
                        if isinstance(item, dict)
                        else None
                    ),
                )

    for index, item in enumerate(response.get("evidence", [])):
        if isinstance(item, dict):
            _add(
                evidence,
                document_id=document_id,
                evidence_id=item.get("evidence_id")
                or f"{document_id}:module_evidence:{index}",
                evidence_type=EvidenceType.DERIVED,
                field=f"module_evidence.{item.get('category', index)}",
                value=item,
                source=f"aadhaar.{item.get('source', 'evidence')}",
                confidence=item.get("confidence"),
                severity=item.get("severity"),
                description=_description(item.get("confidence_basis")),
            )

    forensics = response.get("forensics")
    if isinstance(forensics, dict):
        _add_mapping(
            evidence,
            document_id=document_id,
            prefix="forensics",
            mapping=forensics,
            source="aadhaar.forensics",
            evidence_type=EvidenceType.OBSERVATION,
            unmapped_fields=unmapped_fields,
        )
        for index, region in enumerate(forensics.get("regions", [])):
            if isinstance(region, dict):
                _add(
                    evidence,
                    document_id=document_id,
                    evidence_id=region.get("evidence_id")
                    or f"{document_id}:forensics:region:{index}",
                    evidence_type=EvidenceType.DERIVED,
                    field=f"forensics.region[{index}]",
                    value=region,
                    source="aadhaar.forensics",
                    confidence=region.get("confidence"),
                    severity=region.get("severity"),
                    region=(
                        {"bounding_box": region["bounding_box"]}
                        if region.get("bounding_box") is not None
                        else None
                    ),
                    description=_description(region.get("confidence_basis")),
                )

    screening = response.get("screening")
    if isinstance(screening, dict):
        _add(
            evidence,
            document_id=document_id,
            evidence_id=f"{document_id}:screening:status",
            evidence_type=EvidenceType.DERIVED,
            field="screening.status",
            value=screening.get("status"),
            source="aadhaar.screening",
        )
        _add_mapping(
            evidence,
            document_id=document_id,
            prefix="screening",
            mapping=screening,
            source="aadhaar.screening",
            evidence_type=EvidenceType.DERIVED,
            unmapped_fields=unmapped_fields,
        )

    scores = response.get("scores")
    if isinstance(scores, dict):
        for key in ("coverage_sufficient",):
            _add(
                evidence,
                document_id=document_id,
                evidence_id=f"{document_id}:scores:{key}",
                evidence_type=EvidenceType.DERIVED,
                field=f"scores.{key}",
                value=scores.get(key),
                source="aadhaar.scores",
            )

    processing_status = response.get("module_status")
    if not isinstance(processing_status, str):
        processing_status = "unknown"
    _add(
        evidence,
        document_id=document_id,
        evidence_id=f"{document_id}:module_status",
        evidence_type=EvidenceType.OBSERVATION,
        field="module_status",
        value=processing_status,
        source="aadhaar.processing",
    )

    handled = {
        "case_id", "document_type", "document_variant", "module",
        "module_version", "module_status", "generated_at", "processing",
        "capabilities", "document", "document_security",
        "document_identification", "page_analyses", "quality", "orientation",
        "fields", "number_validation", "qr", "qr_consistency", "photo",
        "biometric", "forensics", "metadata", "offline_ekyc", "validation",
        "contradictions", "evidence", "evidence_relations", "scores",
        "screening", "artifacts", "audit", "privacy", "errors",
    }
    unmapped_fields.extend(
        f"response.{key}" for key in response if key not in handled
    )

    return AadhaarAdapterResult(
        document=Document(
            document_id=document_id,
            document_type="Aadhaar",
            source_module="aadhaar",
            processing_status=processing_status,
        ),
        evidence=evidence,
        raw_response=response,
        error=(
            "Aadhaar module returned errors."
            if response.get("errors")
            else None
        ),
        unmapped_fields=unmapped_fields,
    )


def screen_aadhaar_file(
    image_path: str | Path,
    *,
    timeout: float = 300.0,
    base_url: str = AADHAAR_API_BASE_URL,
) -> AadhaarAdapterResult:
    """Submit one local document to the Aadhaar screening service."""

    path = Path(image_path)
    document_id = path.name
    fallback = Document(
        document_id=document_id,
        document_type="Aadhaar",
        source_module="aadhaar",
        processing_status="error",
    )
    if not path.is_file():
        return AadhaarAdapterResult(
            document=fallback,
            error=f"Aadhaar document file not found: {path}",
        )

    content_type = mimetypes.guess_type(path.name)[0]
    if content_type not in {
        "image/jpeg",
        "image/png",
        "application/pdf",
    }:
        return AadhaarAdapterResult(
            document=Document(
                document_id=document_id,
                document_type="Aadhaar",
                source_module="aadhaar",
                processing_status="invalid_input",
            ),
            error="Aadhaar document must be a JPG, PNG, or PDF file.",
        )

    try:
        with path.open("rb") as document_file:
            response = requests.post(
                f"{base_url.rstrip('/')}{AADHAAR_SCREEN_PATH}",
                files={
                    "document": (path.name, document_file, content_type),
                },
                data={"persist_artifacts": "false"},
                timeout=timeout,
            )
        raw_response: dict[str, Any] | None = None
        try:
            payload = response.json()
            if isinstance(payload, dict):
                raw_response = payload
        except ValueError:
            payload = None

        if response.status_code >= 400:
            return AadhaarAdapterResult(
                document=fallback,
                raw_response=raw_response,
                error=f"Aadhaar service returned HTTP {response.status_code}.",
            )
        if not isinstance(payload, dict):
            return AadhaarAdapterResult(
                document=fallback,
                error="Aadhaar service returned invalid JSON.",
            )

        returned_id = payload.get("case_id")
        try:
            return adapt_aadhaar_response(
                payload,
                document_id=(
                    returned_id
                    if isinstance(returned_id, str) and returned_id
                    else document_id
                ),
            )
        except ValueError as exc:
            return AadhaarAdapterResult(
                document=fallback,
                raw_response=raw_response,
                error=f"Malformed Aadhaar response: {exc}",
            )
    except requests.Timeout:
        return AadhaarAdapterResult(
            document=fallback,
            error="Aadhaar service request timed out.",
        )
    except requests.RequestException as exc:
        return AadhaarAdapterResult(
            document=fallback,
            error=f"Aadhaar service unavailable: {exc}",
        )
