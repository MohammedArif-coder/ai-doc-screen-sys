import { DEMO_CASES } from '../data/demoData'

export function DemoCases({ onSelectDemo, busy }) {
  return (
    <section className="demo-cases-container panel">
      <div className="section-title-row">
        <div>
          <span className="section-badge badge-demo">CONTROLLED DEMONSTRATION MODE</span>
          <h2>Prepared Synthetic Demo Cases</h2>
          <p className="section-sub">
            Demonstrate DAKSH cross-document reasoning even when external document modules are slow or unavailable.
          </p>
        </div>
        <div className="mode-pill-demo">
          <span className="dot demo-dot"></span>
          <span>DEMO WORKLOADS AVAILABLE</span>
        </div>
      </div>

      {/* Core DAKSH Differentiator Banner */}
      <div className="demo-concept-banner">
        <div className="concept-header">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          <strong>Core DAKSH Concept:</strong>
        </div>
        <p className="concept-text">
          "DAKSH does not simply inspect one document in isolation. It normalizes evidence across Passport, Visa, and Aadhaar to detect cross-document contradictions and prioritize human review."
        </p>

        {/* Step-by-step Pipeline Flow Bar */}
        <div className="concept-flow-steps">
          <span className="flow-step">Input Documents</span>
          <span className="flow-arrow">→</span>
          <span className="flow-step">Analysis</span>
          <span className="flow-arrow">→</span>
          <span className="flow-step">Evidence</span>
          <span className="flow-arrow">→</span>
          <span className="flow-step">Contradictions</span>
          <span className="flow-arrow">→</span>
          <span className="flow-step">Risk Status</span>
          <span className="flow-arrow">→</span>
          <span className="flow-step">Explanation</span>
        </div>
      </div>

      <div className="demo-cards-grid-5">
        {DEMO_CASES.map(demo => {
          let badgeClass = 'badge-clear'
          if (demo.statusBadge === 'HIGH_REVIEW') badgeClass = 'badge-high-review'
          if (demo.statusBadge === 'REVIEW') badgeClass = 'badge-review'
          if (demo.statusBadge === 'INCONCLUSIVE') badgeClass = 'badge-inconclusive'

          return (
            <div
              key={demo.id}
              className="demo-card demo-card-5"
              onClick={() => !busy && onSelectDemo(demo)}
            >
              <div className="demo-card-top">
                <span className={`status-pill-sm ${badgeClass}`}>
                  {demo.statusBadge.replace('_', ' ')}
                </span>
                <span className="doc-count-tag">{demo.presetFiles.length} docs</span>
              </div>

              <h3>{demo.title}</h3>
              <p className="demo-desc">{demo.description}</p>

              <div className="demo-files-row">
                {demo.presetFiles.map((file, idx) => (
                  <span className="file-chip" key={idx}>{file}</span>
                ))}
              </div>

              <div className="demo-card-footer">
                <span className="run-link">
                  Load Demo Case
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                  </svg>
                </span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="demo-disclaimer">
        <small>⚠️ <strong>Prototype Disclaimer:</strong> DAKSH is a review-prioritisation research prototype for SIH. Demo cases use synthetic document inputs and do not interact with official government databases.</small>
      </div>
    </section>
  )
}
