const SEV_ICONS = {
  HIGH: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F43F5E" strokeWidth="2.5">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  MEDIUM: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2.5">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  LOW: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#EAB308" strokeWidth="2.5">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  LIMITATION: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2.5">
      <circle cx="12" cy="12" r="10"/>
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  INFO: (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" strokeWidth="2.5">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="16" x2="12" y2="12"/>
      <line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>
  )
}

function parseReasonSeverity(reason) {
  const upper = String(reason).toUpperCase()
  if (upper.includes('HIGH')) return 'HIGH'
  if (upper.includes('MEDIUM')) return 'MEDIUM'
  if (upper.includes('LOW')) return 'LOW'
  if (upper.includes('UNAVAILABLE') || upper.includes('LIMITATION') || upper.includes('NOT_CHECKED') || upper.includes('NOT_CONFIGURED')) return 'LIMITATION'
  return 'INFO'
}

export function WhyThisResult({ reasons, nextActions }) {
  const hasReasons = reasons && reasons.length > 0
  const hasActions = nextActions && nextActions.length > 0

  return (
    <div className="why-result-grid">
      {/* Left: Why This Case */}
      <section className="panel why-panel">
        <div className="section-title-row">
          <div>
            <span className="section-badge">EXPLAINABILITY</span>
            <h2>Why this case requires attention</h2>
          </div>
        </div>

        {hasReasons ? (
          <ul className="reasons-list">
            {reasons.map((reason, idx) => {
              const severity = parseReasonSeverity(reason)
              let sevBadge = 'badge-high'
              if (severity === 'MEDIUM') sevBadge = 'badge-medium'
              if (severity === 'LOW') sevBadge = 'badge-low'
              if (severity === 'LIMITATION') sevBadge = 'badge-limitation'
              if (severity === 'INFO') sevBadge = 'badge-info'

              return (
                <li key={idx} className={`reason-item sev-${severity.toLowerCase()}`}>
                  <div className="reason-icon-col">
                    {SEV_ICONS[severity]}
                  </div>
                  <div className="reason-text-col">
                    <span className={`sev-tag ${sevBadge}`}>{severity}</span>
                    <p className="reason-text">{reason}</p>
                  </div>
                </li>
              )
            })}
          </ul>
        ) : (
          <div className="empty-reasons">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="1.8">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
            <p>No concerning signals or cross-document inconsistencies were identified.</p>
          </div>
        )}
      </section>

      {/* Right: Reviewer Actions */}
      <section className="panel actions-panel">
        <div className="section-title-row">
          <div>
            <span className="section-badge">REVIEWER GUIDANCE</span>
            <h2>Recommended Next Actions</h2>
          </div>
        </div>

        {hasActions ? (
          <ol className="next-actions-list">
            {nextActions.map((action, idx) => (
              <li key={idx} className="action-item">
                <span className="action-step-num">{idx + 1}</span>
                <div className="action-content">
                  <p>{action}</p>
                </div>
              </li>
            ))}
          </ol>
        ) : (
          <div className="empty-actions">
            <p>No mandatory review steps indicated for this case.</p>
          </div>
        )}
      </section>
    </div>
  )
}
