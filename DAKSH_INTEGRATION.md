# DAKSH Integrated Architecture & System Specification

## Overview
DAKSH is a unified Document Authentication & Knowledge-based Screening Hub designed for SIH 2026.
This document details the integrated system architecture, active document modules, orchestration layer, unified API contracts, system health monitoring, and local startup procedures.

---

## Architecture Diagram

```text
                                 DAKSH FRONTEND
                            (React / Vite Single UI)
                                       │
                                       │ HTTP REST
                                       ▼
                            DAKSH ORCHESTRATOR API
                         (daksh-backend on Port 8000)
                                       │
       ┌───────────────────────┼───────────────────────┬───────────────────────┐
       ▼                       ▼                       ▼                       ▼
 Aadhaar Adapter         PAN Adapter             DL Adapter             Passport Adapter
       │                       │                       │                       │
       ▼                       ▼                       ▼                       ▼
Aadhaar Microservice     PAN Microservice        DL Microservice        Passport Microservice
  (Port 8001 / OCR)       (Port 8005 / OCR)       (Port 8004 / OCR)       (Port 8002 / OCR)
```

---

## Active Modules & Service Matrix

| Module | Backend Location | Target Port | API Route | Request Field | Status / Fallback |
|---|---|---|---|---|---|
| **DAKSH Core** | `daksh-backend` | 8000 | `/api/screen-case` | `passport`, `visa`, `aadhaar`, `driving_licence`, `pan` | Central Orchestrator |
| **Aadhaar** | `daksh-backend/app/adapters` | 8001 | `/api/modules/aadhaar` | `file` | Active (Adapter + PaddleOCR) |
| **PAN Card** | `DAKSH_PAN_Module-master` | 8005 | `/api/pan/screen` | `file` | Active (FastAPI wrapper + Adapter) |
| **Driving Licence** | `Driving Licence module/backend` | 8004 | `/api/dl/screen` | `file` | Active (FastAPI service + Adapter) |
| **Passport** | `daksh-backend/app/adapters` | 8002 | `/api/passport/screen` | `file` | Active (Adapter + MRZ/PaddleOCR) |
| **Visa** | `daksh-backend/app/adapters` | 5000 | `/api` | `file` | Active (Adapter + Template OCR) |

---

## System Health & Status Endpoint
The orchestrator backend provides a centralized health monitoring endpoint:
- **`GET /api/system-status`**
  Returns real HTTP connectivity and adapter readiness for all registered document screening modules.

```json
{
  "daksh_engine": "online",
  "api_mode": "real",
  "services": {
    "aadhaar": { "port": 8001, "name": "Aadhaar Module", "status": "online" },
    "pan": { "port": 8005, "name": "PAN Module", "status": "online" },
    "dl": { "port": 8004, "name": "Driving Licence Module", "status": "online" },
    "passport": { "port": 8002, "name": "Passport Module", "status": "online" },
    "visa": { "port": 5000, "name": "Visa Module", "status": "online" }
  }
}
```

---

## Unified Document Screening API Contract

### Request: `POST /api/screen-case`
**Content-Type:** `multipart/form-data`
**Form Fields:**
- `passport`: (Optional) Passport image file
- `visa`: (Optional) Visa image file
- `aadhaar`: (Optional) Aadhaar card image file
- `driving_licence`: (Optional) Driving licence image file
- `pan`: (Optional) PAN card image file

### Response JSON Structure
```json
{
  "case_id": "DAKSH-2026-A1B2C3",
  "documents": [
    {
      "document_id": "05_DL_PRIYA_VERMA.jpg",
      "document_type": "Driving Licence",
      "source_module": "driving_licence",
      "processing_status": "completed"
    }
  ],
  "evidence": [
    {
      "evidence_id": "05_DL_PRIYA_VERMA.jpg:visual_fields:dl_number",
      "document_id": "05_DL_PRIYA_VERMA.jpg",
      "evidence_type": "OBSERVATION",
      "field": "dl_number",
      "value": "DL1420110012345",
      "confidence": 90.0,
      "source": "driving_licence.visual_fields"
    }
  ],
  "contradictions": [],
  "adapter_errors": [],
  "risk_score": 0.1,
  "risk_level": "LOW",
  "decision": "ACCEPT",
  "explanation": "No significant evidence of tampering or document mismatch detected."
}
```

---

## How to Start DAKSH

### Step 1: Start DAKSH Orchestrator Backend (Terminal 1)
```powershell
cd "C:\Users\arifi\OneDrive\Desktop\SIH 2026\DAKSH\daksh-backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Step 2: Start Standalone Microservices (Optional / As Needed)
- **Driving Licence Backend (Port 8004):**
  ```powershell
  cd "C:\Users\arifi\OneDrive\Desktop\SIH 2026\DAKSH\Driving Licence module\backend"
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8004
  ```
- **PAN Microservice (Port 8005):**
  ```powershell
  cd "C:\Users\arifi\OneDrive\Desktop\SIH 2026\DAKSH\DAKSH_PAN_Module-master"
  python -m uvicorn main:app --host 127.0.0.1 --port 8005
  ```

### Step 3: Start DAKSH Frontend (Terminal 2)
```powershell
cd "C:\Users\arifi\OneDrive\Desktop\SIH 2026\DAKSH\daksh-frontend"
npm run dev
```

Navigate browser to `http://localhost:5173`.
