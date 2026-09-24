from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class FieldValue(BaseModel):
    value: Optional[str] = None
    confidence: float = 0.0


class ScreeningRequest(BaseModel):
    case_id: str
    document_type: str


class ScreeningResponse(BaseModel):
    case_id: str
    document_type: str
    fields: Dict[str, FieldValue] = {}
    validation: List[Dict[str, Any]] = []
    forensics: List[Dict[str, Any]] = []
    biometric: Dict[str, Any] = {}
    evidence: List[Dict[str, Any]] = []
    module_status: str = "PENDING"