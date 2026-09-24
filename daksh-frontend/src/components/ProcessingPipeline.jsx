export const PIPELINE_STAGES = [
  { id: 'passport',      label: 'Passport',       desc: 'Visual Zone & MRZ extraction' },
  { id: 'visa',          label: 'Visa',            desc: 'OCR & header field normalization' },
  { id: 'aadhaar',       label: 'Aadhaar',         desc: 'Printed OCR & QR digital signature' },
  { id: 'normalization', label: 'Normalization',   desc: 'Standardizing dates, names, text' },
  { id: 'comparison',    label: 'Comparison',      desc: 'Pairwise field correlation' },
  { id: 'contradiction', label: 'Contradiction',   desc: 'Identifying value mismatches' },
  { id: 'assessment',    label: 'Assessment',      desc: 'Deterministic severity weighting' },
  { id: 'decision',      label: 'Decision',        desc: 'Explainable reviewer priority' }
]

export function ProcessingPipeline({ currentStage, completed, stageStates }) {
  return (
    <section className="pipeline-container panel">
      <div className="pipeline-header">
        <div className="pipeline-title-group">
          <span className="section-badge">PIPELINE EXECUTION</span>
          <h2>DAKSH Evidence Reasoning Chain</h2>
        </div>
        <div className="pipeline-status">
          {completed ? (
            <span className="pill-complete">
              <span className="check-dot">✓</span> Analysis Complete
            </span>
          ) : (
            <span className="pill-processing">
              <span className="spinner-sm"></span>
              Stage {Math.min(currentStage + 1, PIPELINE_STAGES.length)} / {PIPELINE_STAGES.length}
            </span>
          )}
        </div>
      </div>

      {/* Horizontal linear stepper */}
      <div className="pipeline-stepper">
        {PIPELINE_STAGES.map((stage, idx) => {
          let status = 'pending'
          if (stageStates && stageStates[stage.id]) {
            status = stageStates[stage.id]
          } else if (completed) {
            status = 'complete'
          } else if (idx < currentStage) {
            status = 'complete'
          } else if (idx === currentStage) {
            status = 'processing'
          }

          const isLast = idx === PIPELINE_STAGES.length - 1

          return (
            <div key={stage.id} className="stepper-item-wrapper">
              <div className={`stepper-step step-${status}`}>
                <div className="step-indicator">
                  {status === 'complete' && <span className="step-check">✓</span>}
                  {status === 'processing' && <span className="step-spinner"></span>}
                  {status === 'pending' && <span className="step-num">{idx + 1}</span>}
                  {status === 'failed' && <span className="step-fail">✕</span>}
                </div>
                <div className="step-label-group">
                  <span className="step-label">{stage.label}</span>
                  <span className="step-desc">{stage.desc}</span>
                </div>
              </div>
              {!isLast && (
                <div className={`stepper-connector connector-${status === 'complete' ? 'done' : 'pending'}`}>
                  <div className="connector-line"></div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </section>
  )
}
