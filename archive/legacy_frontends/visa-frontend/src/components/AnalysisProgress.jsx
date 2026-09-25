import React from 'react';
import { CheckCircle2, Clock3, Activity } from 'lucide-react';

export default function AnalysisProgress({ loading, result }) {
  const stages = [
    { label: 'OCR Extraction', done: !!result || loading },
    { label: 'Image Quality Analysis', done: !!result || loading },
    { label: 'Consistency Checking', done: !!result },
    { label: 'Risk Engine Synthesis', done: !!result },
  ];

  return (
    <div className="panel pipeline">
      <div className="panel-kicker">SCREENING PIPELINE STATUS</div>
      <div className="pipeline-row">
        {stages.map((stage, idx) => (
          <span key={idx} className={stage.done ? 'pipeline-done' : 'pipeline-idle'}>
            {stage.done ? (
              <CheckCircle2 size={16} />
            ) : loading ? (
              <Activity className="spin" size={16} />
            ) : (
              <Clock3 size={16} />
            )}
            {stage.label}
          </span>
        ))}
      </div>
    </div>
  );
}
