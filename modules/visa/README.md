# DAKSH – Visa Document Screening Module

**DAKSH** (*Document Authentication & Screening Hub*) is an AI-assisted, research-grade prototype system designed for authorized document screeners. It analyzes synthetic visa documents for inconsistencies, image manipulation, missing fields, suspicious formatting, OCR mismatches, and visual authenticity signals.

> **CRITICAL COMPLIANCE & SAFETY NOTICE:**
> This is a research/prototype screening system. Its results are automated signals to assist human review and must NOT be treated as definitive proof of document authenticity or fraud.
> 
> All demonstration documents used in this system are 100% synthetic fictional documents (fictional countries like *Republic of Example*, *Demo Federation*, *Testland*, and fictional names like *ARUN DEMO*). No real government visa templates, seals, passport numbers, MRZ data, or official logos are reproduced. Every generated document carries a prominent `"DEMO – NOT A REAL VISA"` watermark.

---

## 1. Project Overview & Features

- **Synthetic Demo Visa Generator:** Automatically generates 5 distinct synthetic test cases with embedded anomalies:
  - `DEMO-01`: Clean synthetic document baseline (Low Concern)
  - `DEMO-02`: Inconsistent expiry date fields (Date Inconsistency Finding)
  - `DEMO-03`: Intentionally altered text region (Image Manipulation Finding)
  - `DEMO-04`: Mismatched applicant name fields (Identity Mismatch Finding)
  - `DEMO-05`: Low-quality noisy/blurred image (Manual Review Finding)
- **Multi-Phase Screening Pipeline:**
  1. **OCR Text Extraction:** Pytesseract image-to-text with regex field parsing for Applicant Name, Document ID, Issue Date, Expiry Date, Purpose, and Nationality.
  2. **Image Quality Analysis:** OpenCV Laplacian variance blur estimation, resolution scoring, contrast, brightness, and high-pass noise level measurement.
  3. **Error Level Analysis (ELA) & Tamper Detection:** Re-compression pixel delta analysis, edge discontinuity detection, and region bounding box highlight overlay.
  4. **Cross-Field Consistency Verification:** Issue vs. Expiry date range logic, applicant name spelling matching, document ID formatting, and missing field checks.
  5. **Risk Synthesis Engine:** Combines scores into categorized status (`LOW CONCERN`, `REVIEW`, `HIGH CONCERN`) with actionable reasons.
- **Enterprise Dark-Navy Dashboard:** Built with React 18, Vite, Tailwind CSS, Lucide React icons, and Recharts. Includes:
  - Landing Hero Experience with key capabilities overview.
  - Interactive Drag-and-Drop file uploader (PNG, JPG, JPEG).
  - Document Viewer with region highlight overlays and zoom controls.
  - Extracted OCR panel & field consistency table.
  - Recharts signal distribution chart.
  - SQLite audit history log with search and risk level filter tabs.
  - PDF Report Generator using ReportLab with compulsory prototype disclaimers.

---

## 2. Technology Stack

### Frontend
- **Framework:** React.js (v18) + Vite
- **Styling:** Custom Vanilla CSS with Tailwind CSS utilities & HSL dark navy theme
- **Icons:** Lucide React
- **Charts:** Recharts

### Backend
- **Framework:** Python Flask (v3.0) + Flask-CORS
- **Computer Vision & Image Processing:** OpenCV (`opencv-python-headless`), Pillow (`PIL`), NumPy
- **OCR:** Tesseract OCR (`pytesseract`) with deterministic fallback
- **PDF Generation:** ReportLab
- **Database:** SQLite (`daksh.db`)

---

## 3. Project Structure

```
daksh-visa-screening/
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       │
│       ├── components/
│       │   ├── Sidebar.jsx
│       │   ├── Header.jsx
│       │   ├── UploadZone.jsx
│       │   ├── DocumentPreview.jsx
│       │   ├── AnalysisProgress.jsx
│       │   ├── ScoreCard.jsx
│       │   ├── FindingsPanel.jsx
│       │   ├── OCRPanel.jsx
│       │   ├── ConsistencyPanel.jsx
│       │   ├── TamperHeatmap.jsx
│       │   ├── DemoVisaSelector.jsx
│       │   ├── ReportPanel.jsx
│       │   └── StatusBadge.jsx
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── VisaScreening.jsx
│       │   ├── DemoDocuments.jsx
│       │   ├── ScreeningHistory.jsx
│       │   └── Settings.jsx
│       │
│       └── services/
│           └── api.js
│
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── database.py
│   │
│   ├── routes/
│   │   ├── upload_routes.py
│   │   ├── analysis_routes.py
│   │   ├── demo_routes.py
│   │   └── report_routes.py
│   │
│   ├── services/
│   │   ├── ocr_service.py
│   │   ├── image_analysis.py
│   │   ├── tamper_detection.py
│   │   ├── consistency_checker.py
│   │   ├── risk_engine.py
│   │   └── report_generator.py
│   │
│   ├── demo_data/
│   │   ├── demo_visas/
│   │   ├── metadata/
│   │   └── generate_demo_visas.py
│   │
│   └── uploads/
│
├── README.md
└── .gitignore
```

---

## 4. Installation & Quickstart

### Prerequisite
Python 3.9+ and Node.js 18+ installed on your system.

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Generate synthetic demo visa images and metadata
python demo_data/generate_demo_visas.py

# Start Flask backend server (http://localhost:5000)
python app.py
```

*Note on OCR:* Tesseract OCR (`pytesseract`) will automatically extract text if Tesseract is installed on your system `PATH`. If Tesseract is not installed, the backend cleanly uses synthetic metadata fallbacks so the entire workflow operates smoothly without hard external dependencies.

### 2. Frontend Setup

```bash
cd frontend

# Install Node packages
npm install

# Start Vite development server (http://localhost:5173)
npm run dev
```

---

## 5. API Endpoint Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | System status & health check |
| `GET` | `/api/demo/documents` | List all synthetic demo document metadata |
| `GET` | `/api/demo/documents/<id>` | Get specific demo document metadata |
| `GET` | `/api/demo/documents/<id>/image` | Serve synthetic demo document image |
| `POST` | `/api/visa/upload` | Upload a new PNG/JPG document image |
| `GET` | `/api/uploads/<filename>` | Serve uploaded document image |
| `POST` | `/api/visa/analyze` | Execute complete screening pipeline |
| `GET` | `/api/visa/history` | Retrieve past screening audit history from SQLite |
| `POST` | `/api/reports/generate` | Generate and download PDF screening report |

---

## 6. Limitations & Disclaimer

- **Screening Indicators vs. Proof:** Automated findings (Error Level Analysis, blur score, field consistency checks) are screening signals meant to assist human operators. They do not constitute definitive legal proof of fraud or authenticity.
- **Local Prototype Scope:** This software is designed for local demonstration and software testing purposes. No real personal data should be permanently stored in demo environments.
