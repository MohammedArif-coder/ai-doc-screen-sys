import React from 'react';
import { CheckCircle2, AlertTriangle } from 'lucide-react';

export default function ConsistencyPanel({ consistencyData }) {
  const isConsistent = consistencyData?.consistent ?? true;
  const score = consistencyData?.score ?? 100;
  const findings = consistencyData?.findings || [];

  const checks = [
    {
      name: 'EXPIRY DATE Altered Marker Check',
      ok: !findings.some((f) => f.type === 'date_inconsistency'),
      detail: findings.find((f) => f.type === 'date_inconsistency')?.message || 'Expiry date tag valid'
    },
    {
      name: 'VISA NUMBER Integrity Check',
      ok: !findings.some((f) => f.type === 'image_anomaly' && f.message.includes('Visa number')),
      detail: 'Visa number block verified'
    },
    {
      name: 'FULL NAME vs MRZ Line Cross-Check',
      ok: !findings.some((f) => f.type === 'identity_mismatch'),
      detail: findings.find((f) => f.type === 'identity_mismatch')?.message || 'MRZ name matches FULL NAME'
    },
    {
      name: 'Image Quality & Sharpness Check',
      ok: !findings.some((f) => f.type === 'low_quality'),
      detail: findings.find((f) => f.type === 'low_quality')?.message || 'Image resolution optimal'
    },
  ];

  return (
    <div className="panel" style={{ marginTop: '14px' }}>
      <div className="panel-head">
        <div>
          <div className="panel-kicker">DOCUMENT CONSISTENCY CHECKER</div>
          <h2>Official Entry Visa Field Validation</h2>
        </div>
        <span style={{ fontSize: '12px', fontWeight: 600, color: isConsistent ? 'var(--green)' : 'var(--amber)' }}>
          Consistency Score: {score}%
        </span>
      </div>

      <div style={{ display: 'grid', gap: '8px' }}>
        {checks.map((chk, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              padding: '10px 12px',
              background: '#0a1926',
              border: '1px solid var(--line)',
              borderRadius: '6px',
              fontSize: '11px'
            }}
          >
            <div>
              <span style={{ color: '#d0dfeb', fontWeight: 600, display: 'block' }}>{chk.name}</span>
              <small style={{ color: 'var(--muted)', fontSize: '9px' }}>{chk.detail}</small>
            </div>
            <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: chk.ok ? 'var(--green)' : 'var(--amber)' }}>
              {chk.ok ? <CheckCircle2 size={15} /> : <AlertTriangle size={15} />}
              {chk.ok ? 'PASS' : 'SIGNAL'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
