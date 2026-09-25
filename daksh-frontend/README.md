# DAKSH — Document Intelligence & Verification

Main orchestration frontend for DAKSH. Routes individual documents to their
specialised screening modules, and correlates multiple documents through the
DAKSH Intelligence Engine.

## Setup

```bash
npm install
cp .env.example .env   # fill in real backend URLs when ready
npm run dev
```

Runs on `http://localhost:5173`. Without any backend URLs set, every module
runs in **mock mode** — a deterministic demo pipeline and result, clearly
marked "Demo data" in the UI. This is what you want for the SIH demo.

## Architecture

```
src/
  api/
    dakshApi.js          shared fetch wrapper, error type, mock/real switch
    moduleApi.js          verifyDocument(moduleId, file) — individual modules
    multiDocumentApi.js   verifyCase(documents) — the intelligence engine
  config/
    modules.js             central module registry (the frontend contract)
  components/               Header, Sidebar, StatusPill, PipelineSteps
  pages/
    Dashboard, IndividualSelect/Upload/Processing/Result,
    MultiNewCase/Processing/Result, History, SystemStatus
```

**To connect a real module backend:** set its `VITE_*_BACKEND_URL` env var
and set `VITE_API_MODE=real`. `moduleApi.js` and `multiDocumentApi.js` switch
to real `fetch()` calls automatically — no UI changes needed. Status pills
(`Online` / `Not Connected` / `Unavailable`) always reflect actual
connectivity; nothing is faked as online.

**To add a new document type:** add one entry to `MODULES` in
`config/modules.js` (id, name, icon, capabilities, endpoint). Selection,
upload, processing, and result pages all read from the registry — no
per-module UI branching required.

## Design tokens

Defined in `tailwind.config.js`: `brand` (primary navy/blue), `engine` (teal,
reserved for the multi-document/flagship workflow), semantic `success` /
`warning` / `danger` / `info`. Typeface is IBM Plex Sans for UI text and IBM
Plex Mono for case IDs, confidence scores, and tabular data.
