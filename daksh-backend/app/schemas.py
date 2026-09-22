"""Common P6 data contract models."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """How an evidence item was produced."""

    OBSERVATION = "OBSERVATION"
    DERIVED = "DERIVED"
    DECISION = "DECISION"


class EvidenceRelationshipType(str, Enum):
    """Relationship between two evidence items."""

    DERIVED_FROM = "DERIVED_FROM"
    CONTRADICTS = "CONTRADICTS"
    SUPPORTS = "SUPPORTS"
    CORROBORATES = "CORROBORATES"
    OVERLAPS_REGION = "OVERLAPS_REGION"
    DEPENDS_ON = "DEPENDS_ON"


class ScreeningStatus(str, Enum):
    """Case-level screening status."""

    CLEAR = "CLEAR"
    LOW_CONCERN = "LOW_CONCERN"
    REVIEW = "REVIEW"
    HIGH_REVIEW = "HIGH_REVIEW"
    INCONCLUSIVE = "INCONCLUSIVE"


class Document(BaseModel):
    """A document processed by one DAKSH document module."""

    document_id: str
    document_type: str
    source_module: str
    processing_status: str


class Evidence(BaseModel):
    """A normalized observation, derivation, or decision from a module."""

    evidence_id: str
    document_id: str
    evidence_type: EvidenceType
    field: str
    value: Any
    normalized_value: Any | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    quality: float | None = Field(default=None, ge=0.0, le=1.0)
    severity: str | None = None
    source: str
    region: dict[str, Any] | None = None
    description: str | None = None


class EvidenceRelationship(BaseModel):
    """A typed relationship between two evidence items."""

    relationship_type: EvidenceRelationshipType
    source_evidence_id: str
    target_evidence_id: str


class Contradiction(BaseModel):
    """A comparison result between evidence from two documents."""

    contradiction_id: str
    field: str
    document_a: str
    document_b: str
    value_a: Any
    value_b: Any
    normalized_value_a: Any | None = None
    normalized_value_b: Any | None = None
    comparison: str
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    severity: str | None = None
    explanation: str


class ScreeningResult(BaseModel):
    """Explainable case-level output from the DAKSH screening pipeline."""

    status: ScreeningStatus
    review_required: bool
    reasons: list[str] = Field(default_factory=list)
    contradictions: list[Contradiction] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
