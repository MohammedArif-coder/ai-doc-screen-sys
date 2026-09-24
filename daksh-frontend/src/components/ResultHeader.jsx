export function ResultHeader({ result, onReset, isDemo }) {
  const status = result.status || 'INCONCLUSIVE'
  const reviewRequired = result.review_required ?? true
  const contradictionsCount = result.contradictions?.length || 0
  const evidenceCount = result.evidence?.length || 0
  const docsCount = result.documents?.length || 0

  let statusConfig = {
    label: 'HIGH REVIEW',
    badgeClass: 'status-high-review',
    colorVar: '#F43F5E',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F43F5E" strokeWidth="2.2">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
    description: 'High-priority cross-document contradiction detected. Urgent manual verification required.'
  }

  if (status === 'REVIEW') {
    statusConfig = {
      label: 'REVIEW',
      badgeClass: 'status-review',
      colorVar: '#F59E0B',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2.2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      ),
      description: 'Cross-document inconsistency detected. Reviewer verification required.'
    }
  } else if (status === 'LOW_CONCERN') {
    statusConfig = {
      label: 'LOW CONCERN',
      badgeClass: 'status-low-concern',
      colorVar: '#EAB308',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EAB308" strokeWidth="2.2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
      ),
      description: 'Minor evidence signal present. Low review priority.'
    }
  } else if (status === 'CLEAR') {
    statusConfig = {
      label: 'CLEAR',
      badgeClass: 'status-clear',
      colorVar: '#10B981',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="2.2">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      ),
      description: 'No significant cross-document inconsistency detected.'
    }
  } else if (status === 'INCONCLUSIVE') {
    statusConfig = {
      label: 'INCONCLUSIVE',
      badgeClass: 'status-inconclusive',
      colorVar: '#94A3B8',
      icon: (
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="2.2">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      ),
      description: 'Assessment inconclusive due to document quality or incomplete checks.'
    }
  }

  return (
    <section className="result-header-container panel">
      {/* Top meta row: case ID + mode pill + reset button */}
      <div className="result-topbar">
        <div className="result-meta-row">
          <code className="result-case-id">{result.case_id || 'DAKSH-CASE-001'}</code>
          {isDemo ? (
            <span className="mode-pill-demo">
              <span className="dot demo-dot"></span> DEMO MODE · SYNTHETIC CASE
            </span>
          ) : (
            <span className="mode-pill-live">
              <span className="dot live-dot"></span> LIVE ANALYSIS
            </span>
          )}
        </div>
        <button type="button" className="btn-secondary" onClick={onReset}>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
          </svg>
          New Case
        </button>
      </div>

      {/* Primary verdict card */}
      <div className={`prominent-result-card ${statusConfig.badgeClass}`}>
        <div className="result-card-left">
          <div className="status-icon-box">
            {statusConfig.icon}
          </div>
          <div className="status-title-group">
            <div className="status-tag-row">
              <span className="status-main-badge">{statusConfig.label}</span>
              <span className={`review-required-pill ${reviewRequired ? 'req-yes' : 'req-no'}`}>
                {reviewRequired ? 'HUMAN REVIEW REQUIRED' : 'NO REVIEW REQUIRED'}
              </span>
            </div>
            <h2 className="result-headline">{result.headline}</h2>
            <p className="status-sub-desc">{statusConfig.description}</p>
          </div>
        </div>

        <div className="result-card-right">
          <div className="metric-box">
            <span className="metric-val">{contradictionsCount}</span>
            <span className="metric-lbl">Contradictions</span>
          </div>
          <div className="metric-divider"></div>
          <div className="metric-box">
            <span className="metric-val">{evidenceCount}</span>
            <span className="metric-lbl">Evidence Items</span>
          </div>
          <div className="metric-divider"></div>
          <div className="metric-box">
            <span className="metric-val">{docsCount}</span>
            <span className="metric-lbl">Docs Analyzed</span>
          </div>
        </div>
      </div>

      {/* 5-second clarity strip — horizontal chips */}
      <div className="clarity-strip">
        <span className="clarity-strip-label">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          Case Overview
        </span>
        <div className="clarity-chips">
          <div className="clarity-chip">
            <span className="chip-label">Documents</span>
            <span className="chip-value">{result.documents?.map(d => d.document_type).join(', ') || 'Uploaded'}</span>
          </div>
          <span className="chip-sep">→</span>
          <div className="clarity-chip">
            <span className="chip-label">Verdict</span>
            <span className={`chip-value status-text-${status.toLowerCase()}`}>{statusConfig.label}</span>
          </div>
          <span className="chip-sep">→</span>
          <div className="clarity-chip">
            <span className="chip-label">Key Signal</span>
            <span className="chip-value chip-truncate">{result.reasons?.[0] ? result.reasons[0].slice(0, 55) + (result.reasons[0].length > 55 ? '…' : '') : 'Consistent cross-document findings'}</span>
          </div>
          <span className="chip-sep">→</span>
          <div className="clarity-chip">
            <span className="chip-label">Contradictions</span>
            <span className="chip-value">{contradictionsCount > 0 ? `${contradictionsCount} field mismatch${contradictionsCount !== 1 ? 'es' : ''}` : 'None detected'}</span>
          </div>
          <span className="chip-sep">→</span>
          <div className="clarity-chip">
            <span className="chip-label">Action</span>
            <span className="chip-value chip-truncate">{result.next_actions?.[0] || 'No action required'}</span>
          </div>
        </div>
      </div>
    </section>
  )
}
