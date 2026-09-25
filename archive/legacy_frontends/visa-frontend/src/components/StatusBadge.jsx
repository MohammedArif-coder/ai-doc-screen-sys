import React from 'react';

const STATUS_MAP = {
  low_concern: { label: 'LOW CONCERN', tone: 'success' },
  review: { label: 'REVIEW', tone: 'warning' },
  high_concern: { label: 'HIGH CONCERN', tone: 'danger' },
  passed: { label: 'PASSED', tone: 'success' },
  manual_review: { label: 'MANUAL REVIEW', tone: 'warning' },
  normal: { label: 'NORMAL', tone: 'success' },
  suspicious_signal: { label: 'SUSPICIOUS SIGNAL', tone: 'danger' },
};

export default function StatusBadge({ status, children }) {
  const key = (status || '').toLowerCase().replace(/\s+/g, '_');
  const config = STATUS_MAP[key] || { label: (status || 'UNKNOWN').toUpperCase(), tone: 'neutral' };

  return (
    <span className={`badge ${config.tone}`}>
      <span className="badge-dot" />
      {children || config.label}
    </span>
  );
}
