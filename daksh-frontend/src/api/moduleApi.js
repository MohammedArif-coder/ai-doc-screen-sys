import { API_MODE, request, wait, DakshApiError } from './dakshApi.js'
import { getModule, DAKSH_BACKEND_URL } from '../config/modules.js'

// Field name mapping for daksh-backend's POST /api/screen-case
const MODULE_FORM_FIELDS = {
  aadhaar: 'aadhaar',
  pan: 'pan',
  dl: 'driving_licence',
  passport: 'passport',
  visa: 'visa'
}

// Demo/mock results, clearly separated from real API responses.
const MOCK_RESULTS = {
  aadhaar: {
    outcome: 'verified',
    confidence: 0.94,
    fields: [
      { label: 'Name', value: 'Arjun Mehta', confidence: 0.97 },
      { label: 'DOB', value: '12 Jan 2000', confidence: 0.95 },
      { label: 'Aadhaar No.', value: 'XXXX XXXX 4417', confidence: 0.99 },
      { label: 'Address', value: 'Coimbatore, Tamil Nadu', confidence: 0.88 }
    ],
    checks: [
      { label: 'OCR extraction', status: 'pass', detail: 'All fields extracted above threshold.' },
      { label: 'QR / barcode verification', status: 'pass', detail: 'QR payload matches printed fields.' },
      { label: 'Layout forensics', status: 'pass', detail: 'No layout deviation detected.' },
      { label: 'Tampering check', status: 'pass', detail: 'No cloning or splicing artifacts found.' }
    ],
    findings: [
      'Document layout matches the current UIDAI template.',
      'QR payload is internally consistent with printed demographic fields.'
    ]
  },
  pan: {
    outcome: 'review',
    confidence: 0.81,
    fields: [
      { label: 'Name', value: 'ARJUN MEHTA', confidence: 0.96 },
      { label: 'PAN', value: 'ABCDE1234F', confidence: 0.99 },
      { label: 'DOB', value: '12 Jan 2003', confidence: 0.9 }
    ],
    checks: [
      { label: 'OCR extraction', status: 'pass', detail: 'All fields extracted above threshold.' },
      { label: 'Checksum validation', status: 'pass', detail: 'PAN checksum is structurally valid.' },
      { label: 'Layout forensics', status: 'warn', detail: 'Font kerning on DOB line deviates from template.' }
    ],
    findings: ['Minor font-spacing deviation on the date-of-birth line — recommend manual review.']
  },
  dl: {
    outcome: 'verified',
    confidence: 0.91,
    fields: [
      { label: 'Name', value: 'Arjun Mehta', confidence: 0.95 },
      { label: 'DL No.', value: 'TN37 20230004417', confidence: 0.97 },
      { label: 'Valid Till', value: '11 Jan 2043', confidence: 0.93 }
    ],
    checks: [
      { label: 'OCR extraction', status: 'pass', detail: 'All fields extracted above threshold.' },
      { label: 'Layout forensics', status: 'pass', detail: 'No layout deviation detected.' }
    ],
    findings: ['Document is within validity period and matches issuing-state template.']
  },
  passport: {
    outcome: 'verified',
    confidence: 0.96,
    fields: [
      { label: 'Name', value: 'ARJUN MEHTA', confidence: 0.98 },
      { label: 'Passport No.', value: 'P1234567', confidence: 0.99 },
      { label: 'DOB', value: '12 Jan 2000', confidence: 0.97 },
      { label: 'Date of Issue', value: '20 Feb 2020', confidence: 0.94 }
    ],
    checks: [
      { label: 'MRZ parsing', status: 'pass', detail: 'MRZ checksum digits all valid.' },
      { label: 'OCR extraction', status: 'pass', detail: 'Visual zone matches MRZ zone.' },
      { label: 'Layout forensics', status: 'pass', detail: 'No layout deviation detected.' }
    ],
    findings: ['MRZ and visual inspection zone are fully consistent.']
  },
  visa: {
    outcome: 'needs_review',
    confidence: 0.72,
    fields: [
      { label: 'Visa No.', value: 'V998877', confidence: 0.85 },
      { label: 'Issue Date', value: '14 Jan 2000', confidence: 0.8 },
      { label: 'Type', value: 'Tourist', confidence: 0.9 }
    ],
    checks: [
      { label: 'OCR extraction', status: 'pass', detail: 'Extraction confidence below preferred threshold.' },
      { label: 'Template matching', status: 'warn', detail: 'Partial match against issuing-country template.' }
    ],
    findings: ['Low-confidence template match — recommend cross-checking against the passport record.']
  }
}

/**
 * Normalize raw response from DAKSH Orchestration Backend into UI contract
 */
function normalizeDakshResponse(raw, moduleId) {
  if (raw.error && (!raw.evidence || raw.evidence.length === 0)) {
    throw new DakshApiError(raw.error, { stage: 'server', retryable: false })
  }
  if (Array.isArray(raw.adapter_errors) && raw.adapter_errors.length > 0 && (!raw.evidence || raw.evidence.length === 0)) {
    throw new DakshApiError(raw.adapter_errors.join('; '), { stage: 'server', retryable: false })
  }

  const decisionMap = { ACCEPT: 'verified', REVIEW: 'review', REJECT: 'needs_review' }
  const outcome = decisionMap[raw.decision] || (raw.evidence?.length > 0 ? 'verified' : 'review')

  const fields = []
  const checks = []
  const findings = []

  let confSum = 0
  let confCount = 0

  if (Array.isArray(raw.evidence)) {
    for (const ev of raw.evidence) {
      const conf = typeof ev.confidence === 'number' ? (ev.confidence > 1 ? ev.confidence / 100 : ev.confidence) : 0.9
      confSum += conf
      confCount++

      if (ev.evidence_type === 'OBSERVATION' || ev.field) {
        fields.push({
          label: ev.field ? ev.field.replace(/_/g, ' ').toUpperCase() : 'Field',
          value: typeof ev.value === 'object' ? JSON.stringify(ev.value) : String(ev.value),
          confidence: conf
        })
      }

      const status = ev.severity === 'HIGH' ? 'fail' : ev.severity === 'MEDIUM' ? 'warn' : 'pass'
      checks.push({
        label: ev.field ? ev.field.replace(/_/g, ' ') : 'Verification Check',
        status,
        detail: ev.description || `${ev.source || 'Module'} reported ${status}`
      })

      if (ev.description) {
        findings.push(ev.description)
      }
    }
  }

  if (raw.explanation) {
    findings.push(raw.explanation)
  }

  if (findings.length === 0) {
    findings.push(`Verified through DAKSH orchestration adapter. Status: ${raw.decision || 'Completed'}.`)
  }

  const confidence = confCount > 0 ? confSum / confCount : 0.90

  return {
    outcome,
    confidence: Math.round(confidence * 100) / 100,
    fields,
    checks: checks.length > 0 ? checks : [{ label: 'DAKSH Adapter Inspection', status: 'pass', detail: 'Document processed by DAKSH Backend.' }],
    findings,
    demo: false
  }
}

/**
 * verifyDocument(moduleId, file, { onStage })
 * Common contract for every individual-verification module.
 */
export async function verifyDocument(moduleId, file, { onStage } = {}) {
  const mod = getModule(moduleId)
  if (!mod) throw new DakshApiError('Unknown module.', { stage: 'upload', retryable: false })

  const backendUrl = mod.endpoint || DAKSH_BACKEND_URL

  if (API_MODE === 'real' && backendUrl) {
    onStage?.('upload')
    const form = new FormData()
    const formKey = MODULE_FORM_FIELDS[moduleId] || 'file'
    form.append(formKey, file)

    onStage?.('ocr')
    await wait(300)
    onStage?.('validation')

    const screenEndpoint = `${backendUrl}/api/screen-case`
    const rawResult = await request(screenEndpoint, { method: 'POST', body: form })

    onStage?.('result')
    return normalizeDakshResponse(rawResult, moduleId)
  }

  // Mock/demo path
  const stages = ['upload', 'ocr', 'validation', 'forensics', 'result']
  for (const stage of stages) {
    onStage?.(stage)
    await wait(450)
  }
  const mock = MOCK_RESULTS[moduleId] || MOCK_RESULTS.aadhaar
  return { ...mock, demo: true }
}
