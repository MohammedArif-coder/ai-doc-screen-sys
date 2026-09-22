import React from 'react';
import { AlertTriangle, Info } from 'lucide-react';

export default function TamperHeatmap({ tamperAnalysis }) {
  const regions = tamperAnalysis?.regions || [];
  const detected = tamperAnalysis?.signal_detected || false;

  return (
    <div className="tamper-heatmap-container" style={{ marginTop: '14px' }}>
      <div className="panel-head" style={{ marginBottom: '10px' }}>
        <h3 style={{ fontSize: '13px', margin: 0, color: '#e2edf2', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={15} color={detected ? 'var(--amber)' : 'var(--green)'} />
          Potential Manipulation Signals
        </h3>
        <span style={{ fontSize: '10px', color: 'var(--muted)' }}>
          {tamperAnalysis?.category || 'NORMAL'}
        </span>
      </div>

      {regions.length > 0 ? (
        <div style={{ display: 'grid', gap: '8px' }}>
          {regions.map((region, idx) => (
            <div
              key={idx}
              style={{
                background: '#182b3a',
                border: '1px solid #2b4f69',
                borderRadius: '6px',
                padding: '8px 12px',
                fontSize: '11px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <span style={{ color: 'var(--amber)', fontWeight: 600 }}>
                ⚠ {region.label}
              </span>
              <span style={{ fontSize: '9px', color: '#9bb1c0' }}>
                X: {region.x}% · Y: {region.y}%
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ fontSize: '11px', color: 'var(--muted)', padding: '8px 0' }}>
          No local image region manipulation signals detected in visual check.
        </div>
      )}

      <div className="notice" style={{ marginTop: '12px' }}>
        <Info size={15} />
        <span>
          {tamperAnalysis?.disclaimer || 'Screening signals indicate areas for human verification, not conclusive proof of fraud.'}
        </span>
      </div>
    </div>
  );
}
