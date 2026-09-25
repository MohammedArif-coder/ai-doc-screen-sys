// Central DAKSH module registry.
// Every individual-verification document type is described here through a
// common contract. Nothing in the UI should hardcode module-specific logic —
// components read from this list instead. Swap `status` / `endpoint` per
// environment; never invent capabilities a module doesn't actually report.

export const MODULE_STATUS = {
  ONLINE: 'online',
  DEGRADED: 'degraded',
  UNAVAILABLE: 'unavailable',
  NOT_CONNECTED: 'not_connected'
}

export const DAKSH_BACKEND_URL = import.meta.env.VITE_DAKSH_BACKEND_URL || 'http://127.0.0.1:8000'

export const MODULES = [
  {
    id: 'aadhaar',
    name: 'Aadhaar',
    shortName: 'AADHAAR',
    description: 'UIDAI identity document. QR verification, demographic OCR, and layout forensics.',
    icon: 'IdCard',
    supportedFormats: ['JPG', 'PNG', 'PDF'],
    endpoint: DAKSH_BACKEND_URL,
    status: MODULE_STATUS.ONLINE,
    capabilities: ['OCR', 'QR Verification', 'Layout Forensics', 'Field Validation']
  },
  {
    id: 'pan',
    name: 'PAN Card',
    shortName: 'PAN',
    description: 'Income Tax Department identifier. Checksum validation and font/layout tamper checks.',
    icon: 'CreditCard',
    supportedFormats: ['JPG', 'PNG', 'PDF'],
    endpoint: DAKSH_BACKEND_URL,
    status: MODULE_STATUS.ONLINE,
    capabilities: ['OCR', 'Checksum Validation', 'Layout Forensics']
  },
  {
    id: 'dl',
    name: 'Driving Licence',
    shortName: 'DL',
    description: 'State transport authority licence. Field extraction and hologram/layout inspection.',
    icon: 'Car',
    supportedFormats: ['JPG', 'PNG', 'PDF'],
    endpoint: DAKSH_BACKEND_URL,
    status: MODULE_STATUS.ONLINE,
    capabilities: ['OCR', 'Field Validation', 'Layout Forensics']
  },
  {
    id: 'passport',
    name: 'Passport',
    shortName: 'PASSPORT',
    description: 'MRZ parsing, checksum verification, and biographic page forensics.',
    icon: 'BookUser',
    supportedFormats: ['JPG', 'PNG', 'PDF'],
    endpoint: DAKSH_BACKEND_URL,
    status: MODULE_STATUS.ONLINE,
    capabilities: ['OCR', 'MRZ Parsing', 'Checksum Validation', 'Layout Forensics']
  },
  {
    id: 'visa',
    name: 'Visa',
    shortName: 'VISA',
    description: 'Visa sticker / stamp verification against issuing-country templates.',
    icon: 'StampIcon',
    supportedFormats: ['JPG', 'PNG', 'PDF'],
    endpoint: DAKSH_BACKEND_URL,
    status: MODULE_STATUS.ONLINE,
    capabilities: ['OCR', 'Template Matching']
  }
]

export const MULTI_DOC_ENGINE = {
  id: 'daksh-engine',
  name: 'DAKSH Intelligence Engine',
  endpoint: DAKSH_BACKEND_URL,
  status: MODULE_STATUS.ONLINE,
  stages: [
    'Field Extraction',
    'Entity Matching',
    'Cross-Document Comparison',
    'Contradiction Analysis',
    'Risk Aggregation',
    'Explainable Decision'
  ]
}

export function getModule(id) {
  return MODULES.find((m) => m.id === id)
}
