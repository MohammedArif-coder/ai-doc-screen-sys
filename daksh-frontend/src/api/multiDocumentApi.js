import { API_MODE, request, wait, DakshApiError } from './dakshApi.js'
import { MULTI_DOC_ENGINE, DAKSH_BACKEND_URL } from '../config/modules.js'

const MODULE_FORM_FIELDS = {
  aadhaar: 'aadhaar',
  pan: 'pan',
  dl: 'driving_licence',
  passport: 'passport',
  visa: 'visa'
}

const MOCK_CASE_RESULT = {
  demo: true,
  caseId: 'DAKSH-2025-0417',
  applicant: 'Arjun Mehta',
  overallRisk: 'high',
  documentsAnalyzed: 5,
  fieldsCompared: 18,
  contradictionsFound: 1,
  comparison: [
    { field: 'Name', values: { Aadhaar: 'Arjun Mehta', PAN: 'ARJUN MEHTA', DL: 'Arjun Mehta', Passport: 'ARJUN MEHTA' }, status: 'match' },
    { field: 'Date of Birth', values: { Aadhaar: '—', PAN: '12 Jan 2003', DL: '—', Passport: '12 Jan 2000' }, status: 'review' },
    { field: 'Address', values: { Aadhaar: 'Coimbatore, TN', PAN: '—', DL: 'Coimbatore, TN', Passport: '—' }, status: 'match' },
    { field: 'Document No.', values: { Aadhaar: 'XXXX 4417', PAN: 'ABCDE1234F', DL: 'TN37…4417', Passport: 'P1234567' }, status: 'valid' }
  ],
  contradictions: [
    {
      title: 'Date of birth mismatch',
      severity: 'high',
      sourceA: { label: 'Passport', value: '12 Jan 2000' },
      sourceB: { label: 'Visa', value: '14 Jan 2000' },
      explanation: 'The same identity attribute carries conflicting values across two source documents.'
    }
  ],
  network: [
    { id: 'aadhaar', label: 'Aadhaar' },
    { id: 'pan', label: 'PAN' },
    { id: 'dl', label: 'Driving Licence' },
    { id: 'passport', label: 'Passport' },
    { id: 'visa', label: 'Visa' }
  ]
}

/**
 * Normalize raw DAKSH backend case output for MultiResult UI
 */
function normalizeDakshCaseResponse(raw, documents) {
  if (raw.error && (!raw.documents || raw.documents.length === 0)) {
    throw new DakshApiError(raw.error, { stage: 'server', retryable: false })
  }

  const caseId = raw.case_id || `DAKSH-${Math.random().toString(36).substring(2, 10).toUpperCase()}`
  const overallRisk = (raw.risk_level || 'LOW').toLowerCase()

  const docCount = raw.documents?.length || documents.length
  const evidenceCount = raw.evidence?.length || 0
  const contradictionsFound = raw.contradictions?.length || 0

  const network = (raw.documents || []).map((d) => ({
    id: d.source_module || d.document_type.toLowerCase(),
    label: d.document_type
  }))

  if (network.length === 0) {
    documents.forEach((d) => {
      network.push({ id: d.moduleId, label: d.moduleId.toUpperCase() })
    })
  }

  // Extract applicant name if present in evidence
  let applicantName = 'Case Applicant'
  const nameEvidence = raw.evidence?.find((e) => e.field && e.field.toLowerCase().includes('name'))
  if (nameEvidence && nameEvidence.value) {
    applicantName = String(nameEvidence.value)
  }

  // Build comparison table rows from extracted evidence
  const fieldMap = {}
  if (Array.isArray(raw.evidence)) {
    for (const ev of raw.evidence) {
      if (ev.field && ev.value) {
        const fieldName = ev.field.replace(/_/g, ' ').toUpperCase()
        if (!fieldMap[fieldName]) {
          fieldMap[fieldName] = {}
        }
        const docLabel = ev.document_id || ev.source || 'Doc'
        fieldMap[fieldName][docLabel] = String(ev.value)
      }
    }
  }

  const comparison = []
  for (const [field, values] of Object.entries(fieldMap)) {
    const valList = Object.values(values)
    const isMismatch = valList.length > 1 && new Set(valList.map((v) => v.toLowerCase())).size > 1
    comparison.push({
      field,
      values,
      status: isMismatch ? 'review' : 'match'
    })
  }

  if (comparison.length === 0) {
    comparison.push({
      field: 'Extracted Fields',
      values: { 'DAKSH Engine': `${evidenceCount} evidence items extracted` },
      status: 'valid'
    })
  }

  // Map backend contradictions
  const contradictions = (raw.contradictions || []).map((c) => ({
    title: c.field ? `${c.field.replace(/_/g, ' ')} mismatch` : 'Cross-document contradiction',
    severity: c.severity === 'HIGH' ? 'high' : 'medium',
    sourceA: { label: c.document_a || 'Doc A', value: c.value_a || 'Val A' },
    sourceB: { label: c.document_b || 'Doc B', value: c.value_b || 'Val B' },
    explanation: c.explanation || 'Conflict detected between documents.'
  }))

  return {
    demo: false,
    caseId,
    applicant: applicantName,
    overallRisk: overallRisk === 'reject' ? 'high' : overallRisk === 'review' ? 'medium' : overallRisk,
    documentsAnalyzed: docCount,
    fieldsCompared: Math.max(evidenceCount, comparison.length * docCount),
    contradictionsFound,
    comparison,
    contradictions,
    network
  }
}

/**
 * verifyCase(documents, { onStage })
 * Common contract for the multi-document / cross-correlation workflow.
 * `documents` is an array of { moduleId, file }.
 */
export async function verifyCase(documents, { onStage } = {}) {
  if (!documents?.length) {
    throw new DakshApiError('Add at least one document to start a case.', { stage: 'upload', retryable: false })
  }

  const backendUrl = MULTI_DOC_ENGINE.endpoint || DAKSH_BACKEND_URL

  if (API_MODE === 'real' && backendUrl) {
    onStage?.(MULTI_DOC_ENGINE.stages[0])
    const form = new FormData()

    documents.forEach((d) => {
      const formKey = MODULE_FORM_FIELDS[d.moduleId] || 'file'
      form.append(formKey, d.file)
    })

    for (let i = 1; i < MULTI_DOC_ENGINE.stages.length - 1; i++) {
      onStage?.(MULTI_DOC_ENGINE.stages[i])
      await wait(300)
    }

    const endpoint = `${backendUrl}/api/screen-case`
    const rawResult = await request(endpoint, { method: 'POST', body: form })

    onStage?.('done')
    return normalizeDakshCaseResponse(rawResult, documents)
  }

  for (const stage of MULTI_DOC_ENGINE.stages) {
    onStage?.(stage)
    await wait(500)
  }
  return MOCK_CASE_RESULT
}

export const DEMO_CASES = [
  { id: 'demo-01', title: 'Demo Case 01', description: 'All documents consistent', risk: 'low' },
  { id: 'demo-02', title: 'Demo Case 02', description: 'Contradictory date of birth', risk: 'high' },
  { id: 'demo-03', title: 'Demo Case 03', description: 'Potential tampering flagged', risk: 'high' },
  { id: 'demo-04', title: 'Demo Case 04', description: 'Incomplete evidence set', risk: 'medium' }
]
