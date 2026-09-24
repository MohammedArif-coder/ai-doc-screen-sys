"""P6 orchestration for processing Passport, Visa, Aadhaar, Driving Licence, and PAN Card cases."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from app.adapters.aadhaar_adapter import (
    AadhaarAdapterResult,
    screen_aadhaar_file,
)
from app.adapters.driving_licence_adapter import (
    DrivingLicenceAdapterResult,
    screen_driving_licence_file,
)
from app.adapters.pan_adapter import (
    PANAdapterResult,
    screen_pan_file,
)
from app.adapters.passport_adapter import (
    PassportAdapterResult,
    screen_passport_file,
)
from app.adapters.visa_adapter import VisaAdapterResult, screen_visa_file
from app.schemas import Contradiction, Document, Evidence
from app.services.contradiction_engine import detect_contradictions


PassportRunner = Callable[[str | Path], PassportAdapterResult]
VisaRunner = Callable[[str | Path], VisaAdapterResult]
AadhaarRunner = Callable[[str | Path], AadhaarAdapterResult]
DLRunner = Callable[[str | Path], DrivingLicenceAdapterResult]
PANRunner = Callable[[str | Path], PANAdapterResult]
ContradictionDetector = Callable[[list[Evidence]], list[Contradiction]]


@dataclass
class CaseServiceResult:
    """Combined module output for one multi-document case."""

    passport_result: PassportAdapterResult | None
    visa_result: VisaAdapterResult | None
    passport_document: Document | None
    visa_document: Document | None
    evidence: list[Evidence] = field(default_factory=list)
    contradictions: list[Contradiction] = field(default_factory=list)
    adapter_errors: list[str] = field(default_factory=list)
    aadhaar_result: AadhaarAdapterResult | None = None
    aadhaar_document: Document | None = None
    driving_licence_result: DrivingLicenceAdapterResult | None = None
    driving_licence_document: Document | None = None
    pan_result: PANAdapterResult | None = None
    pan_document: Document | None = None


def _failed_document(document_type: str, source_module: str, image_path: str | Path) -> Document:
    return Document(
        document_id=Path(image_path).name,
        document_type=document_type,
        source_module=source_module,
        processing_status="error",
    )


def run_case(
    passport_image_path: str | Path | None = None,
    visa_image_path: str | Path | None = None,
    *,
    passport_runner: PassportRunner = screen_passport_file,
    visa_runner: VisaRunner = screen_visa_file,
    aadhaar_image_path: str | Path | None = None,
    aadhaar_runner: AadhaarRunner = screen_aadhaar_file,
    driving_licence_image_path: str | Path | None = None,
    driving_licence_runner: DLRunner = screen_driving_licence_file,
    pan_image_path: str | Path | None = None,
    pan_runner: PANRunner = screen_pan_file,
    contradiction_detector: ContradictionDetector = detect_contradictions,
) -> CaseServiceResult:
    """Run available document adapters, merge evidence, and detect contradictions."""

    passport_result: PassportAdapterResult | None = None
    visa_result: VisaAdapterResult | None = None
    aadhaar_result: AadhaarAdapterResult | None = None
    driving_licence_result: DrivingLicenceAdapterResult | None = None
    pan_result: PANAdapterResult | None = None
    adapter_errors: list[str] = []

    if passport_image_path is not None:
        try:
            passport_result = passport_runner(passport_image_path)
            if passport_result.error:
                adapter_errors.append(f"passport: {passport_result.error}")
        except (OSError, RuntimeError, ValueError) as exc:
            adapter_errors.append(f"passport: {exc}")

    if visa_image_path is not None:
        try:
            visa_result = visa_runner(visa_image_path)
            if visa_result.error:
                adapter_errors.append(f"visa: {visa_result.error}")
        except (OSError, RuntimeError, ValueError) as exc:
            adapter_errors.append(f"visa: {exc}")

    if aadhaar_image_path is not None:
        try:
            aadhaar_result = aadhaar_runner(aadhaar_image_path)
            if aadhaar_result.error:
                adapter_errors.append(f"aadhaar: {aadhaar_result.error}")
        except (OSError, RuntimeError, ValueError) as exc:
            adapter_errors.append(f"aadhaar: {exc}")

    if driving_licence_image_path is not None:
        try:
            driving_licence_result = driving_licence_runner(driving_licence_image_path)
            if driving_licence_result.error:
                adapter_errors.append(f"driving_licence: {driving_licence_result.error}")
        except (OSError, RuntimeError, ValueError) as exc:
            adapter_errors.append(f"driving_licence: {exc}")

    if pan_image_path is not None:
        try:
            pan_result = pan_runner(pan_image_path)
            if pan_result.error:
                adapter_errors.append(f"pan: {pan_result.error}")
        except (OSError, RuntimeError, ValueError) as exc:
            adapter_errors.append(f"pan: {exc}")

    passport_document = (
        passport_result.document
        if passport_result is not None
        else (
            _failed_document("Passport", "passport", passport_image_path)
            if passport_image_path is not None
            else None
        )
    )
    visa_document = (
        visa_result.document
        if visa_result is not None
        else (
            _failed_document("Visa", "visa", visa_image_path)
            if visa_image_path is not None
            else None
        )
    )
    aadhaar_document = (
        aadhaar_result.document
        if aadhaar_result is not None
        else (
            _failed_document("Aadhaar", "aadhaar", aadhaar_image_path)
            if aadhaar_image_path is not None
            else None
        )
    )
    dl_document = (
        driving_licence_result.document
        if driving_licence_result is not None
        else (
            _failed_document("Driving Licence", "driving_licence", driving_licence_image_path)
            if driving_licence_image_path is not None
            else None
        )
    )
    pan_document = (
        pan_result.document
        if pan_result is not None
        else (
            _failed_document("PAN", "pan", pan_image_path)
            if pan_image_path is not None
            else None
        )
    )

    evidence = []
    if passport_result is not None:
        evidence.extend(passport_result.evidence)
    if visa_result is not None:
        evidence.extend(visa_result.evidence)
    if aadhaar_result is not None:
        evidence.extend(aadhaar_result.evidence)
    if driving_licence_result is not None:
        evidence.extend(driving_licence_result.evidence)
    if pan_result is not None:
        evidence.extend(pan_result.evidence)

    contradictions = contradiction_detector(evidence)

    return CaseServiceResult(
        passport_result=passport_result,
        visa_result=visa_result,
        passport_document=passport_document,
        visa_document=visa_document,
        aadhaar_result=aadhaar_result,
        aadhaar_document=aadhaar_document,
        driving_licence_result=driving_licence_result,
        driving_licence_document=dl_document,
        pan_result=pan_result,
        pan_document=pan_document,
        evidence=evidence,
        contradictions=contradictions,
        adapter_errors=adapter_errors,
    )
