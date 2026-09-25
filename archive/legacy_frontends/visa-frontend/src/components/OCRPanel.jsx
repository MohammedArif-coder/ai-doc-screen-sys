import React, { useState } from 'react';
import { FileText, ClipboardCheck } from 'lucide-react';

export default function OCRPanel({ ocrData, onOpenReport }) {
  const [tab, setTab] = useState('fields');
  const fields = ocrData?.fields || {};
  const confidence = ocrData?.confidence || 0;
  const rawText = ocrData?.text || '';

  const fieldLabels = {
    applicant_name: 'FULL NAME',
    passport_no: 'PASSPORT NO',
    visa_number: 'VISA NUMBER',
    visa_type: 'VISA TYPE',
    issue_date: 'ISSUE DATE',
    expiry_date: 'EXPIRY DATE',
    nationality: 'NATIONALITY',
  };

  return (
    <div className="panel ocr">
      <div className="panel-head">
        <h2>Extracted Fields (OCR)</h2>
        <span>Confidence: {confidence}%</span>
      </div>

      <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', borderBottom: '1px solid var(--line)', paddingBottom: '8px' }}>
        <button
          className={`text-btn ${tab === 'fields' ? 'active' : ''}`}
          onClick={() => setTab('fields')}
          style={{ fontWeight: tab === 'fields' ? 700 : 400, color: tab === 'fields' ? 'var(--blue)' : 'var(--muted)' }}
        >
          Extracted Visa Fields
        </button>
        <button
          className={`text-btn ${tab === 'raw' ? 'active' : ''}`}
          onClick={() => setTab('raw')}
          style={{ fontWeight: tab === 'raw' ? 700 : 400, color: tab === 'raw' ? 'var(--blue)' : 'var(--muted)' }}
        >
          Raw OCR Text
        </button>
      </div>

      {tab === 'fields' ? (
        <div>
          {Object.entries(fieldLabels).map(([key, label]) => (
            <div className="field" key={key}>
              <span>{label}</span>
              <strong style={{ color: fields[key]?.includes('ALTERED') ? 'var(--red)' : '#d7e6ea' }}>
                {fields[key] || 'Not readable'}
              </strong>
            </div>
          ))}
        </div>
      ) : (
        <pre
          style={{
            background: '#091520',
            border: '1px solid var(--line)',
            borderRadius: '6px',
            padding: '12px',
            fontSize: '11px',
            color: '#a8c2d2',
            whiteSpace: 'pre-wrap',
            maxHeight: '220px',
            overflow: 'auto'
          }}
        >
          {rawText || 'No raw OCR text extracted.'}
        </pre>
      )}

      {onOpenReport && (
        <button className="secondary-btn" onClick={onOpenReport} style={{ width: '100%', justifyContent: 'center', marginTop: '14px' }}>
          <ClipboardCheck size={16} /> Open Screening Report
        </button>
      )}
    </div>
  );
}
