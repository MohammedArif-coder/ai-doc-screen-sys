 # DAKSH PAN Module

Python modules for PAN document extraction, OCR, validation, forensics, biometric comparison, and pipeline processing.

## Project files

- `pan_pipeline.py` coordinates the PAN processing workflow.
- `pan_extractor.py` extracts document data.
- `pan_ocr.py` handles OCR-related processing.
- `pan_validator.py` validates extracted PAN fields.
- `pan_forensics.py` checks document integrity signals.
- `pan_biometric.py` and `compare_pan_images.py` support image comparison.
- `create_pan_test_cases.py` and `create_tampered_pan.py` generate local test data.

## Setup

Use Python 3.10 or newer, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Add only synthetic or anonymized PAN samples to `input/` before running the scripts. Do not commit real identity documents or generated results.

## Status

This repository is prepared for local Git initialization and publishing to GitHub.
