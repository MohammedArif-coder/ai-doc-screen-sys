import React from 'react';

export default function DemoVisaSelector({ demos = [], selectedId, onSelect, loading }) {
  const cases = demos.length
    ? demos
    : [
        { id: 'DEMO-01', description: 'Clean Baseline (JOHN DOE, Tourist Visa V987654321)', anomaly: 'clean' },
        { id: 'DEMO-02', description: 'Expiration Date Altered Mismatch ([ ALTERED / EXPIRATION MISMATCH ])', anomaly: 'date_mismatch' },
        { id: 'DEMO-03', description: 'Invalid Visa Number Block Altered ([ ALTERED / INVALID VISA NO ])', anomaly: 'altered_region' },
        { id: 'DEMO-04', description: 'MRZ Name Conflict (FULL NAME JANE DOE vs MRZ ALICE)', anomaly: 'identity_mismatch' },
        { id: 'DEMO-05', description: 'Blurred Image (Low Resolution / Manual Review Required)', anomaly: 'low_quality' },
      ];

  return (
    <div className="demo-select">
      <label>OFFICIAL ENTRY VISA DEMO LIBRARY</label>
      <select
        value={selectedId || ''}
        onChange={(e) => onSelect(e.target.value)}
        disabled={loading}
      >
        <option value="" disabled>
          -- Choose an Official Entry Visa case --
        </option>
        {cases.map((demo) => (
          <option key={demo.id} value={demo.id}>
            {demo.id} · {demo.description}
          </option>
        ))}
      </select>
    </div>
  );
}
