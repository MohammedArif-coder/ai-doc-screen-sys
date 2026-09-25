import React from 'react';
import { CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';

export default function FindingsPanel({ findings = [] }) {
  return (
    <div className="panel findings">
      <div className="panel-head">
        <h2>Detected Findings</h2>
        <span>{findings.length} signal(s)</span>
      </div>

      {findings.length === 0 ? (
        <div style={{ padding: '16px 0', fontSize: '11px', color: 'var(--muted)' }}>
          No findings or inconsistencies detected.
        </div>
      ) : (
        findings.map((finding, idx) => {
          const isOk = finding.severity === 'low';
          return (
            <div className="finding" key={idx}>
              <div className={`finding-icon ${isOk ? 'ok' : 'warn'}`}>
                {isOk ? <CheckCircle2 size={16} /> : <AlertTriangle size={16} />}
              </div>
              <div>
                <strong>{finding.message}</strong>
                <small>
                  SEVERITY: {finding.severity ? finding.severity.toUpperCase() : 'MEDIUM'} · LOCATION: {finding.location || 'Document'}
                </small>
              </div>
            </div>
          );
        })
      )}
    </div>
  );
}
