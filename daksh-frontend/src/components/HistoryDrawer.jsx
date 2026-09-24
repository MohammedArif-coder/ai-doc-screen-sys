export function HistoryDrawer({ history, onSelectCase, onClearHistory }) {
  if (!history || history.length === 0) {
    return (
      <section className="panel history-container">
        <div className="section-title-row">
          <div>
            <span className="section-badge">SESSION HISTORY</span>
            <h2>Screening History</h2>
            <p className="section-sub">Past document screening cases evaluated in this session.</p>
          </div>
        </div>
        <div className="empty-state-box">
          <p>No screening cases recorded in history yet.</p>
        </div>
      </section>
    )
  }

  return (
    <section className="panel history-container">
      <div className="section-title-row">
        <div>
          <span className="section-badge">SESSION HISTORY</span>
          <h2>Screening History</h2>
          <p className="section-sub">Review and revisit past case analysis results in this session.</p>
        </div>
        <button type="button" className="btn-secondary-sm" onClick={onClearHistory}>
          Clear History
        </button>
      </div>

      <div className="history-cards-list">
        {history.map((item, idx) => {
          const status = item.status || 'INCONCLUSIVE'
          let statusClass = 'badge-clear'
          if (status === 'HIGH_REVIEW') statusClass = 'badge-high-review'
          if (status === 'REVIEW') statusClass = 'badge-review'
          if (status === 'LOW_CONCERN') statusClass = 'badge-low-concern'
          if (status === 'INCONCLUSIVE') statusClass = 'badge-inconclusive'

          return (
            <div key={idx} className="history-card" onClick={() => onSelectCase(item)}>
              <div className="history-card-top">
                <span className="case-id-code">{item.case_id}</span>
                <span className={`status-pill-sm ${statusClass}`}>{status.replace('_', ' ')}</span>
              </div>
              
              <div className="history-meta-row">
                <span>Timestamp: {new Date(item.timestamp || Date.now()).toLocaleTimeString()}</span>
                <span>Docs: {item.documents?.length || 0}</span>
                <span>Contradictions: {item.contradictions?.length || 0}</span>
                <span>Evidence: {item.evidence?.length || 0}</span>
              </div>

              <div className="history-headline">
                <p>{item.headline}</p>
              </div>

              <div className="history-footer">
                <span className="reopen-link">Open Case Result →</span>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
