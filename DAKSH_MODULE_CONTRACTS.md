# DAKSH Authoritative Module Contracts

This document contains the verified source-code API contracts, ports, endpoints, request fields, response structures, health checks, and startup commands for all 5 authoritative document screening modules and the central DAKSH backend.

---

## 1. Aadhaar Screening Module

- **Module Directory**: `aadhaar-screening-module-main/aadhaar-screening-module-main/backend/`
- **Framework**: FastAPI (`app.main:app`)
- **Port**: `8001`
- **HTTP Method**: `POST`
- **Screening Endpoint**: `/api/modules/aadhaar`
- **Request Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `document` (UploadFile, **Required**): Aadhaar image or PDF document
  - `reference_face` (UploadFile, Optional): Reference face image for verification
  - `offline_ekyc` (UploadFile, Optional): Offline eKYC XML or ZIP file
  - `case_id` (Form string, Optional): Unique case identifier
  - `persist_artifacts` (Form boolean/string, Optional): Flag to persist debug artifacts
- **Expected Response**:
  ```json
  {
    "case_id": "string",
    "document_type": "AADHAAR",
    "fields": {
      "name": { "value": "string", "confidence": 0.0, "bounding_box": [...] },
      "dob": { "value": "string", "confidence": 0.0 },
      "aadhaar_number": { "value": "string", "confidence": 0.0 },
      "gender": { "value": "string" },
      "address": { "value": "string" }
    },
    "quality": { "score": 0.0 },
    "qr": { "detected": true, "fields": {...} },
    "forensics": { "findings": [...] },
    "screening": { "status": "PASS / REVIEW / FAIL" },
    "scores": { "coverage_sufficient": true },
    "module_status": "COMPLETE"
  }
  ```
- **Health Endpoint**: `GET /api/health`
- **Health Response**: `{"status": "ok", "service": "daksh-aadhaar-p3", ...}`
- **Startup Command**:
  ```bash
  uvicorn app.main:app --host 127.0.0.1 --port 8001
  ```

---

## 2. Passport Screening Module

- **Module Directory**: `daksh-passport-main/`
- **Framework**: FastAPI (`app.main:app`)
- **Port**: `8002`
- **HTTP Method**: `POST`
- **Screening Endpoint**: `/api/passport/screen`
- **Request Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `file` (UploadFile, **Required**): Passport page image (JPG/PNG)
- **Expected Response**:
  ```json
  {
    "status": "no_consistency_issue_detected / manual_review",
    "visual_fields": {
      "passport_number": "string",
      "surname": "string",
      "given_names": "string",
      "dob": "string",
      "expiry_date": "string"
    },
    "mrz": {
      "line1": "string",
      "line2": "string",
      "parsed": { "passport_number": "string", "dob": "string", ... }
    },
    "mrz_validation": { "line1_length": 44, "line2_length": 44, "checks": {...} },
    "consistency": [...],
    "forensics": {...},
    "summary": { "mrz_validation_failures": 0, "field_mismatches": 0 }
  }
  ```
- **Health Endpoint**: `GET /api/health`
- **Health Response**: `{"status": "ok", "module": "passport"}`
- **Startup Command**:
  ```bash
  uvicorn app.main:app --host 127.0.0.1 --port 8002
  ```

---

## 3. Visa Screening Module

- **Module Directory**: `ai-doc-screen-sys/ai-doc-screen-sys/backend/`
- **Framework**: Flask (`app.py`)
- **Port**: `5000`
- **HTTP Method**: `POST` (Two-step upload & analyze workflow)
- **Screening Endpoints**:
  1. `POST /api/visa/upload`
     - **Content-Type**: `multipart/form-data`
     - **Field**: `file` (UploadFile)
     - **Response**: `{"upload_id": "string", "filename": "string"}`
  2. `POST /api/visa/analyze`
     - **Content-Type**: `application/json`
     - **Body**: `{"upload_id": "string"}`
- **Expected Response**:
  ```json
  {
    "document_id": "string",
    "document_name": "string",
    "document_type": "Official Entry Visa",
    "verdict": "VERIFIED / SUSPICIOUS",
    "authenticity_score": 95.0,
    "status": "PASS / REVIEW / FAIL",
    "scores": { "authenticity": 95.0, "ocr": 90.0, "consistency": 100.0, "image_quality": 95.0 },
    "findings": [...],
    "tamper_analysis": { "signal_detected": false, "category": "CLEAR" },
    "ocr": { "fields": { "applicant_name": "...", "passport_no": "...", "visa_number": "..." } },
    "image_analysis": { "score": 95.0 },
    "consistency": { "score": 100.0 },
    "reason": "string"
  }
  ```
- **Health Endpoint**: `GET /api/health`
- **Health Response**: `{"status": "online", "system": "DAKSH Visa Document Screening Hub", ...}`
- **Startup Command**:
  ```bash
  python app.py
  ```

---

## 4. Driving Licence Screening Module

- **Module Directory**: `Driving Licence module/backend/`
- **Framework**: FastAPI (`app.main:app`)
- **Port**: `8004`
- **HTTP Method**: `POST`
- **Screening Endpoint**: `/api/dl/screen` (also `/api/screen`)
- **Request Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `file` (UploadFile, **Required**): Driving licence image (JPG/PNG)
- **Expected Response**:
  ```json
  {
    "success": true,
    "filename": "string",
    "result": {
      "document_type": "DRIVING_LICENCE",
      "ocr_text": "string",
      "ocr": { "average_confidence": 0.85, "word_count": 50 },
      "fields": {
        "name": { "value": "string", "confidence": 0.9 },
        "date_of_birth": { "value": "string", "confidence": 0.9 },
        "licence_number": { "value": "string", "confidence": 0.9 },
        "issue_date": { "value": "string", "confidence": 0.9 },
        "valid_until": { "value": "string", "confidence": 0.9 },
        "vehicle_class": { "value": "string", "confidence": 0.9 }
      },
      "validation": [...],
      "qr_barcode": {...},
      "forensics": {...},
      "biometric": {...},
      "tampering": {...},
      "contradictions": [...],
      "evidence": [...],
      "risk": {...},
      "explanation": {...},
      "module_status": "COMPLETE"
    }
  }
  ```
- **Health Endpoint**: `GET /api/health`
- **Health Response**: `{"status": "healthy", "project": "DAKSH"}`
- **Startup Command**:
  ```bash
  uvicorn app.main:app --host 127.0.0.1 --port 8004
  ```

---

## 5. PAN Card Screening Module

- **Module Directory**: `DAKSH_PAN_Module-master/`
- **Framework**: FastAPI (`main:app`)
- **Port**: `8005`
- **HTTP Method**: `POST`
- **Screening Endpoint**: `/api/pan/screen` (also `/api/screen`)
- **Request Content-Type**: `multipart/form-data`
- **Request Fields**:
  - `file` (UploadFile, **Required**): PAN card image (JPG/PNG)
- **Expected Response**:
  ```json
  {
    "success": true,
    "filename": "string",
    "result": {
      "document_type": "PAN",
      "fields": {
        "pan_number": "string",
        "name": "string",
        "father_name": "string",
        "dob": "string"
      },
      "validation": [...],
      "biometric": {...},
      "forensics": {...},
      "tampering": {...},
      "risk": {...}
    },
    "fields": {...},
    "visual_fields": {...},
    "status": "completed"
  }
  ```
- **Health Endpoint**: `GET /api/health`
- **Health Response**: `{"status": "healthy", "service": "DAKSH PAN Module"}`
- **Startup Command**:
  ```bash
  uvicorn main:app --host 127.0.0.1 --port 8005
  ```

---

## 6. DAKSH Central Backend

- **Module Directory**: `daksh-backend/`
- **Framework**: FastAPI (`app.main:app`)
- **Port**: `8000`
- **HTTP Method**: `POST`
- **Screening Endpoint**: `/api/screen-case`
- **Request Content-Type**: `multipart/form-data`
- **Request Fields** (At least one required):
  - `passport` (UploadFile)
  - `visa` (UploadFile)
  - `aadhaar` (UploadFile)
  - `driving_licence` (UploadFile)
  - `pan` (UploadFile)
- **Health Endpoints**:
  - `GET /api/health` -> `{"status": "ok", "service": "DAKSH P6 API"}`
  - `GET /api/system-status` -> `{"daksh_engine": "online", "services": {...}}`
- **Startup Command**:
  ```bash
  uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```
