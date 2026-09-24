/**
 * Preconfigured Synthetic Demo Cases for DAKSH Screening Pipeline
 * Strictly matches the backend `ScreeningResult` contract schema.
 */

export const DEMO_CASES = [
  {
    id: 'demo-matching',
    title: '1. Matching Documents',
    description: 'Passport, Visa, and Aadhaar documents with fully consistent details across all sources.',
    statusBadge: 'CLEAR',
    presetFiles: ['PASSPORT_MATCH.JPG', 'VISA_MATCH.JPG', 'AADHAAR_MATCH.JPG', 'DL_PRIYA_VERMA.JPG', 'PAN_PRIYA_VERMA.JPG'],
    data: {
      case_id: 'DAKSH-DEMO-MATCH01',
      status: 'CLEAR',
      review_required: false,
      headline: 'No significant inconsistency detected',
      reasons: [
        'All cross-document identity fields match between Passport, Visa, Aadhaar, Driving Licence, and PAN.',
        'MRZ checksums verified successfully.',
        'Aadhaar QR signature verified.'
      ],
      next_actions: [
        'No additional action is indicated by the available evidence.'
      ],
      supporting_evidence_ids: ['passport.mrz:1', 'visa.ocr:1', 'aadhaar.qr:1', 'dl.ocr:1', 'pan.ocr:1'],
      supporting_contradiction_ids: [],
      adapter_errors: [],
      documents: [
        {
          document_id: 'passport-demo-01',
          document_type: 'Passport',
          source_module: 'passport_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'visa-demo-01',
          document_type: 'Visa',
          source_module: 'visa_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'aadhaar-demo-01',
          document_type: 'Aadhaar',
          source_module: 'aadhaar_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'dl-demo-01',
          document_type: 'Driving Licence',
          source_module: 'driving_licence_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'pan-demo-01',
          document_type: 'PAN',
          source_module: 'pan_adapter',
          processing_status: 'completed'
        }
      ],
      contradictions: [],
      evidence: [
        {
          evidence_id: 'p-name-01',
          document_id: 'passport-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'name',
          value: 'RAHUL SHARMA',
          normalized_value: 'rahul sharma',
          confidence: 0.98,
          quality: 0.95,
          severity: null,
          source: 'passport.visual_fields',
          description: 'Name extracted from Passport Visual Inspection Zone'
        },
        {
          evidence_id: 'p-dob-01',
          document_id: 'passport-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'dob',
          value: '1995-06-15',
          normalized_value: '1995-06-15',
          confidence: 0.99,
          quality: 0.96,
          severity: null,
          source: 'passport.mrz',
          description: 'Date of birth extracted from Passport MRZ Line 2'
        },
        {
          evidence_id: 'p-num-01',
          document_id: 'passport-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'passport_number',
          value: 'Z8942103',
          normalized_value: 'z8942103',
          confidence: 0.99,
          quality: 0.98,
          severity: null,
          source: 'passport.mrz',
          description: 'Passport Number extracted from MRZ'
        },
        {
          evidence_id: 'v-name-01',
          document_id: 'visa-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'applicant_name',
          value: 'RAHUL SHARMA',
          normalized_value: 'rahul sharma',
          confidence: 0.96,
          quality: 0.92,
          severity: null,
          source: 'visa.ocr',
          description: 'Applicant name extracted from Visa OCR'
        },
        {
          evidence_id: 'v-passnum-01',
          document_id: 'visa-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'passport_no',
          value: 'Z8942103',
          normalized_value: 'z8942103',
          confidence: 0.97,
          quality: 0.94,
          severity: null,
          source: 'visa.ocr',
          description: 'Passport number extracted from Visa header'
        },
        {
          evidence_id: 'a-name-01',
          document_id: 'aadhaar-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'printed.name',
          value: 'Rahul Sharma',
          normalized_value: 'rahul sharma',
          confidence: 0.94,
          quality: 0.90,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Name from printed text on front Aadhaar card'
        },
        {
          evidence_id: 'a-dob-01',
          document_id: 'aadhaar-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'printed.dob',
          value: '15/06/1995',
          normalized_value: '1995-06-15',
          confidence: 0.95,
          quality: 0.91,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Date of Birth printed on front Aadhaar card'
        },
        {
          evidence_id: 'a-qr-name-01',
          document_id: 'aadhaar-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'qr.name',
          value: 'Rahul Sharma',
          normalized_value: 'rahul sharma',
          confidence: 1.0,
          quality: 1.0,
          severity: null,
          source: 'aadhaar.qr',
          description: 'Name extracted from digitally signed Aadhaar Secure QR Code'
        },
        {
          evidence_id: 'a-qr-dob-01',
          document_id: 'aadhaar-demo-01',
          evidence_type: 'OBSERVATION',
          field: 'qr.dob',
          value: '15-06-1995',
          normalized_value: '1995-06-15',
          confidence: 1.0,
          quality: 1.0,
          severity: null,
          source: 'aadhaar.qr',
          description: 'Date of Birth extracted from Secure QR Code'
        }
      ]
    }
  },
  {
    id: 'demo-dob-contradiction',
    title: '2. DOB Contradiction',
    description: 'Passport date of birth (14/08/2002) differs from Aadhaar printed date of birth (15/08/2002).',
    statusBadge: 'HIGH_REVIEW',
    presetFiles: ['PASSPORT_DOB_A.JPG', 'AADHAAR_DOB_B.JPG'],
    data: {
      case_id: 'DAKSH-DEMO-DOB002',
      status: 'HIGH_REVIEW',
      review_required: true,
      headline: 'High-priority inconsistency requires manual verification',
      reasons: [
        'Contradiction passport-demo-02:aadhaar-demo-02:dob is HIGH severity for dob: The date of birth differs between the Passport evidence (p-dob-02, source passport.mrz) and Aadhaar evidence (a-dob-02, source aadhaar.printed).'
      ],
      next_actions: [
        'Perform manual review of the high-priority contradiction or finding.',
        'Verify the affected date of birth fields against the original physical documents.'
      ],
      supporting_evidence_ids: ['p-dob-02', 'a-dob-02'],
      supporting_contradiction_ids: ['passport-demo-02:aadhaar-demo-02:dob'],
      adapter_errors: [],
      documents: [
        {
          document_id: 'passport-demo-02',
          document_type: 'Passport',
          source_module: 'passport_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'aadhaar-demo-02',
          document_type: 'Aadhaar',
          source_module: 'aadhaar_adapter',
          processing_status: 'completed'
        }
      ],
      contradictions: [
        {
          contradiction_id: 'passport-demo-02:aadhaar-demo-02:dob',
          field: 'dob',
          document_a: 'passport-demo-02',
          document_b: 'aadhaar-demo-02',
          value_a: '14/08/2002',
          value_b: '15/08/2002',
          normalized_value_a: '2002-08-14',
          normalized_value_b: '2002-08-15',
          comparison: 'MISMATCH',
          confidence: null,
          severity: 'HIGH',
          evidence_ids: ['p-dob-02', 'a-dob-02'],
          explanation: 'Date of birth differs between Passport (14/08/2002) and Aadhaar (15/08/2002). Confidence was unavailable for one or both source evidence items.'
        }
      ],
      evidence: [
        {
          evidence_id: 'p-name-02',
          document_id: 'passport-demo-02',
          evidence_type: 'OBSERVATION',
          field: 'name',
          value: 'PRIYA SUNDARAM',
          normalized_value: 'priya sundaram',
          confidence: 0.97,
          quality: 0.94,
          severity: null,
          source: 'passport.visual_fields',
          description: 'Name extracted from Passport Visual Inspection Zone'
        },
        {
          evidence_id: 'p-dob-02',
          document_id: 'passport-demo-02',
          evidence_type: 'OBSERVATION',
          field: 'dob',
          value: '14/08/2002',
          normalized_value: '2002-08-14',
          confidence: null,
          quality: 0.92,
          severity: null,
          source: 'passport.mrz',
          description: 'Date of birth recorded on Passport MRZ Line 2'
        },
        {
          evidence_id: 'p-num-02',
          document_id: 'passport-demo-02',
          evidence_type: 'OBSERVATION',
          field: 'passport_number',
          value: 'K5819034',
          normalized_value: 'k5819034',
          confidence: 0.99,
          quality: 0.96,
          severity: null,
          source: 'passport.mrz',
          description: 'Passport number extracted from MRZ'
        },
        {
          evidence_id: 'a-name-02',
          document_id: 'aadhaar-demo-02',
          evidence_type: 'OBSERVATION',
          field: 'printed.name',
          value: 'Priya Sundaram',
          normalized_value: 'priya sundaram',
          confidence: 0.93,
          quality: 0.88,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Name from printed front face of Aadhaar card'
        },
        {
          evidence_id: 'a-dob-02',
          document_id: 'aadhaar-demo-02',
          evidence_type: 'OBSERVATION',
          field: 'printed.dob',
          value: '15/08/2002',
          normalized_value: '2002-08-15',
          confidence: null,
          quality: 0.89,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Date of birth printed on front side of Aadhaar card'
        }
      ]
    }
  },
  {
    id: 'demo-multiple-contradictions',
    title: '3. Multiple Contradictions',
    description: 'Passport Number differs between Passport & Visa, and Name differs between Passport & Aadhaar.',
    statusBadge: 'HIGH_REVIEW',
    presetFiles: ['PASSPORT_MAIN.JPG', 'VISA_CONFLICT.JPG', 'AADHAAR_NAME_DIFF.JPG'],
    data: {
      case_id: 'DAKSH-DEMO-MULTI03',
      status: 'HIGH_REVIEW',
      review_required: true,
      headline: 'High-priority inconsistency requires manual verification',
      reasons: [
        'Contradiction passport-demo-03:visa-demo-03:passport_number is HIGH severity for passport_number: The passport number differs between Passport (L9810234) and Visa (M9810234).',
        'Contradiction passport-demo-03:aadhaar-demo-03:name is MEDIUM severity for name: The name differs between Passport evidence (ANAND VERMA) and Aadhaar evidence (ANAND KUMAR VERMA).'
      ],
      next_actions: [
        'Perform manual review of the high-priority passport number contradiction.',
        'Cross-check Visa application reference code and applicant name variant with original issuer registry.'
      ],
      supporting_evidence_ids: ['p-num-03', 'v-num-03', 'p-name-03', 'a-name-03'],
      supporting_contradiction_ids: [
        'passport-demo-03:visa-demo-03:passport_number',
        'passport-demo-03:aadhaar-demo-03:name'
      ],
      adapter_errors: [],
      documents: [
        {
          document_id: 'passport-demo-03',
          document_type: 'Passport',
          source_module: 'passport_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'visa-demo-03',
          document_type: 'Visa',
          source_module: 'visa_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'aadhaar-demo-03',
          document_type: 'Aadhaar',
          source_module: 'aadhaar_adapter',
          processing_status: 'completed'
        }
      ],
      contradictions: [
        {
          contradiction_id: 'passport-demo-03:visa-demo-03:passport_number',
          field: 'passport_number',
          document_a: 'passport-demo-03',
          document_b: 'visa-demo-03',
          value_a: 'L9810234',
          value_b: 'M9810234',
          normalized_value_a: 'l9810234',
          normalized_value_b: 'm9810234',
          comparison: 'MISMATCH',
          confidence: 0.98,
          severity: 'HIGH',
          evidence_ids: ['p-num-03', 'v-num-03'],
          explanation: 'The passport number differs between the Passport evidence (L9810234, source passport.mrz) and Visa evidence (M9810234, source visa.ocr).'
        },
        {
          contradiction_id: 'passport-demo-03:aadhaar-demo-03:name',
          field: 'name',
          document_a: 'passport-demo-03',
          document_b: 'aadhaar-demo-03',
          value_a: 'ANAND VERMA',
          value_b: 'ANAND KUMAR VERMA',
          normalized_value_a: 'anand verma',
          normalized_value_b: 'anand kumar verma',
          comparison: 'MISMATCH',
          confidence: 0.94,
          severity: 'MEDIUM',
          evidence_ids: ['p-name-03', 'a-name-03'],
          explanation: 'Name differs between Passport (ANAND VERMA) and Aadhaar (ANAND KUMAR VERMA).'
        }
      ],
      evidence: [
        {
          evidence_id: 'p-num-03',
          document_id: 'passport-demo-03',
          evidence_type: 'OBSERVATION',
          field: 'passport_number',
          value: 'L9810234',
          normalized_value: 'l9810234',
          confidence: 0.99,
          quality: 0.96,
          severity: null,
          source: 'passport.mrz',
          description: 'Passport number from MRZ zone'
        },
        {
          evidence_id: 'v-num-03',
          document_id: 'visa-demo-03',
          evidence_type: 'OBSERVATION',
          field: 'passport_no',
          value: 'M9810234',
          normalized_value: 'm9810234',
          confidence: 0.98,
          quality: 0.94,
          severity: null,
          source: 'visa.ocr',
          description: 'Passport reference printed on Visa'
        },
        {
          evidence_id: 'p-name-03',
          document_id: 'passport-demo-03',
          evidence_type: 'OBSERVATION',
          field: 'name',
          value: 'ANAND VERMA',
          normalized_value: 'anand verma',
          confidence: 0.97,
          quality: 0.95,
          severity: null,
          source: 'passport.visual_fields',
          description: 'Name from Passport visual field'
        },
        {
          evidence_id: 'a-name-03',
          document_id: 'aadhaar-demo-03',
          evidence_type: 'OBSERVATION',
          field: 'printed.name',
          value: 'ANAND KUMAR VERMA',
          normalized_value: 'anand kumar verma',
          confidence: 0.95,
          quality: 0.91,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Printed name on front of Aadhaar card'
        }
      ]
    }
  },
  {
    id: 'demo-poor-quality',
    title: '4. Poor Quality',
    description: 'Aadhaar QR signature verification was unavailable due to low resolution input.',
    statusBadge: 'INCONCLUSIVE',
    presetFiles: ['PASSPORT_BLURRY.JPG', 'AADHAAR_LOWRES.JPG'],
    data: {
      case_id: 'DAKSH-DEMO-INCON04',
      status: 'INCONCLUSIVE',
      review_required: true,
      headline: 'Assessment inconclusive because document quality is insufficient',
      reasons: [
        'Evidence e-aadhaar-qr indicates poor quality for qr.signature; the check may require better input.',
        'Aadhaar QR signature verification was unavailable.'
      ],
      next_actions: [
        'Obtain a clearer document image or rerun unavailable checks.',
        'Verify physical document hologram and security elements under magnification.'
      ],
      supporting_evidence_ids: ['e-aadhaar-qr'],
      supporting_contradiction_ids: [],
      adapter_errors: [
        'aadhaar: QR signature verification unavailable'
      ],
      documents: [
        {
          document_id: 'passport-demo-04',
          document_type: 'Passport',
          source_module: 'passport_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'aadhaar-demo-04',
          document_type: 'Aadhaar',
          source_module: 'aadhaar_adapter',
          processing_status: 'partial'
        }
      ],
      contradictions: [],
      evidence: [
        {
          evidence_id: 'p-name-04',
          document_id: 'passport-demo-04',
          evidence_type: 'OBSERVATION',
          field: 'name',
          value: 'VIKRAM ADITYA',
          normalized_value: 'vikram aditya',
          confidence: 0.72,
          quality: 0.48,
          severity: null,
          source: 'passport.visual_fields',
          description: 'Low-resolution extraction of Passport name'
        },
        {
          evidence_id: 'e-aadhaar-qr',
          document_id: 'aadhaar-demo-04',
          evidence_type: 'DERIVED',
          field: 'qr.signature',
          value: 'NOT_AVAILABLE',
          normalized_value: null,
          confidence: null,
          quality: 0.32,
          severity: 'LOW',
          source: 'aadhaar.qr_verification',
          description: 'Aadhaar QR signature payload could not be decoded due to pixelation'
        }
      ]
    }
  },
  {
    id: 'demo-module-failure',
    title: '5. Module Failure',
    description: 'Passport adapter module experienced a processing error; Visa and Aadhaar evidence remain fully analyzed.',
    statusBadge: 'REVIEW',
    presetFiles: ['PASSPORT_CORRUPT.JPG', 'VISA_VALID.JPG', 'AADHAAR_VALID.JPG'],
    data: {
      case_id: 'DAKSH-DEMO-MODFAIL05',
      status: 'REVIEW',
      review_required: true,
      headline: 'Cross-document inconsistency requires review',
      reasons: [
        'passport: adapter processing failed (Passport analysis unavailable).',
        'Contradiction visa-demo-05:aadhaar-demo-05:name is MEDIUM severity for applicant_name: Name differs between Visa evidence (SUNIL KUMAR) and Aadhaar evidence (SUNIL K).'
      ],
      next_actions: [
        'Perform manual review of the reported contradiction between Visa and Aadhaar.',
        'Resubmit a clean Passport scan to complete the Passport module check.'
      ],
      supporting_evidence_ids: ['v-name-05', 'a-name-05'],
      supporting_contradiction_ids: ['visa-demo-05:aadhaar-demo-05:name'],
      adapter_errors: [
        'passport: adapter processing failed'
      ],
      documents: [
        {
          document_id: 'passport-demo-05',
          document_type: 'Passport',
          source_module: 'passport_adapter',
          processing_status: 'failed'
        },
        {
          document_id: 'visa-demo-05',
          document_type: 'Visa',
          source_module: 'visa_adapter',
          processing_status: 'completed'
        },
        {
          document_id: 'aadhaar-demo-05',
          document_type: 'Aadhaar',
          source_module: 'aadhaar_adapter',
          processing_status: 'completed'
        }
      ],
      contradictions: [
        {
          contradiction_id: 'visa-demo-05:aadhaar-demo-05:name',
          field: 'applicant_name',
          document_a: 'visa-demo-05',
          document_b: 'aadhaar-demo-05',
          value_a: 'SUNIL KUMAR',
          value_b: 'SUNIL K',
          normalized_value_a: 'sunil kumar',
          normalized_value_b: 'sunil k',
          comparison: 'MISMATCH',
          confidence: 0.95,
          severity: 'MEDIUM',
          evidence_ids: ['v-name-05', 'a-name-05'],
          explanation: 'Applicant name differs between Visa OCR (SUNIL KUMAR) and Aadhaar printed text (SUNIL K).'
        }
      ],
      evidence: [
        {
          evidence_id: 'v-name-05',
          document_id: 'visa-demo-05',
          evidence_type: 'OBSERVATION',
          field: 'applicant_name',
          value: 'SUNIL KUMAR',
          normalized_value: 'sunil kumar',
          confidence: 0.96,
          quality: 0.92,
          severity: null,
          source: 'visa.ocr',
          description: 'Applicant name from Visa OCR header'
        },
        {
          evidence_id: 'a-name-05',
          document_id: 'aadhaar-demo-05',
          evidence_type: 'OBSERVATION',
          field: 'printed.name',
          value: 'SUNIL K',
          normalized_value: 'sunil k',
          confidence: 0.94,
          quality: 0.89,
          severity: null,
          source: 'aadhaar.printed',
          description: 'Name from front side of Aadhaar card'
        }
      ]
    }
  }
]
