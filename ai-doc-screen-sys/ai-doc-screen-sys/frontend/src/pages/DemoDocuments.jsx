import React from 'react';
import { ArrowUpRight } from 'lucide-react';
import { api } from '../services/api';

export default function DemoDocuments({ demos = [], onOpenDemo }) {
  const casesList = demos.length
    ? demos
    : [
        { id: 'DEMO-01', description: 'Clean Baseline (JOHN DOE, Tourist Visa V987654321)', anomaly: 'clean' },
        { id: 'DEMO-02', description: 'Expiration Date Altered Mismatch ([ ALTERED / EXPIRATION MISMATCH ])', anomaly: 'date_mismatch' },
        { id: 'DEMO-03', description: 'Invalid Visa Number Block Altered ([ ALTERED / INVALID VISA NO ])', anomaly: 'altered_region' },
        { id: 'DEMO-04', description: 'MRZ Name Conflict (FULL NAME JANE DOE vs MRZ ALICE)', anomaly: 'identity_mismatch' },
        { id: 'DEMO-05', description: 'Blurred Image (Low Resolution / Manual Review Required)', anomaly: 'low_quality' },
      ];

  return (
    <div className="demos-page">
      <div className="section-title">
        <div>
          <div className="eyebrow">OFFICIAL ENTRY VISA SYNTHETIC SUITE</div>
          <h1>Demo Visa Documents</h1>
          <p>Fictional Official Entry Visa test cases matching user template specifications.</p>
        </div>
      </div>

      <div className="demo-grid">
        {casesList.map((demo, index) => {
          const isClean = demo.anomaly === 'clean';
          const imgUrl = api.imageUrl(`/api/demo/documents/${demo.id}/image`);

          return (
            <div className="demo-card" key={demo.id}>
              <div className="demo-image">
                <img src={imgUrl} alt={`Official Entry Visa ${demo.id}`} />
                <span className="case-number">0{index + 1}</span>
              </div>

              <div className="demo-card-body">
                <div className="demo-card-top">
                  <strong>{demo.id}</strong>
                  <span className={`case-state ${isClean ? 'clean' : ''}`}>
                    {isClean ? 'CLEAN BASELINE' : 'ANOMALY CASE'}
                  </span>
                </div>

                <h3>{demo.description}</h3>
                <p style={{ fontSize: '11px', color: 'var(--muted)', margin: '8px 0 14px' }}>
                  Anomaly Mode: <strong style={{ color: '#c0d2de' }}>{demo.anomaly || 'N/A'}</strong>
                </p>

                <button
                  className="text-btn"
                  onClick={() => onOpenDemo(demo.id)}
                  style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                >
                  Open in screening workspace <ArrowUpRight size={15} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
