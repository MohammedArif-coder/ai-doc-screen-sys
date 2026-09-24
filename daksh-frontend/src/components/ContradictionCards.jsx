import { useState } from 'react'

export function ContradictionCards({ contradictions, evidence = [], onSelectEvidenceId }) {
  const [expandedIds, setExpandedIds] = useState({})
  const [showEvidenceTree, setShowEvidenceTree] = useState({})

  if (!contradictions || contradictions.length === 0) {
    return (
      <section className="panel contradictions-container">
        <div className="section-title-row">
          <div>
            <span className="section-badge">CROSS-DOCUMENT COMPARISON</span>
            <h2>Contradictions Register</h2>
          </div>
          <span className="count-pill clear-count">0 Detected</span>
        </div>
        <div className="empty-state-box">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#10B981" strokeWidth="1.8">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
            <polyline points="22 4 12 14.01 9 11.01"/>
          </svg>
          <h4>No Cross-Document Inconsistency Detected</h4>
          <p>The normalized evidence extracted from submitted documents is mutually consistent.</p>
        </div>
      </section>
    )
  }

  const toggleExpand = (id) => setExpandedIds(prev => ({ ...prev, [id]: !prev[id] }))
  const toggleTree = (id) => setShowEvidenceTree(prev => ({ ...prev, [id]: !prev[id] }))

  return (
    <section className="panel contradictions-container">
      <div className="section-title-row">
        <div>
          <span className="section-badge badge-warning">CROSS-DOCUMENT COMPARISON</span>
          <h2>Contradictions Register</h2>
          <p className="section-sub">Field-by-field mismatches with visual provenance and evidence traceability.</p>
        </div>
        <span className="count-pill warning-count">{contradictions.length} Contradiction{contradictions.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="contradiction-cards-list">
        {contradictions.map((item) => {
          const isExpanded = expandedIds[item.contradiction_id] !== false // Default open
          const isTreeOpen = showEvidenceTree[item.contradiction_id] ?? true
          const severity = item.severity || 'MEDIUM'

          let sevBadge = 'badge-high'
          if (severity === 'MEDIUM') sevBadge = 'badge-medium'
          if (severity === 'LOW') sevBadge = 'badge-low'

          const confidenceDisplay = (item.confidence === null || item.confidence === undefined)
            ? 'Unavailable'
            : `${(item.confidence * 100).toFixed(0)}%`

          const supportingEvidenceItems = (evidence || []).filter(e =>
            (item.evidence_ids && item.evidence_ids.includes(e.evidence_id)) ||
            (e.document_id === item.document_a && e.field === item.field) ||
            (e.document_id === item.document_b && e.field === item.field)
          )

          const evA = supportingEvidenceItems.find(e => e.document_id === item.document_a)
          const evB = supportingEvidenceItems.find(e => e.document_id === item.document_b)

          return (
            <article key={item.contradiction_id} className={`contradiction-card sev-${severity.toLowerCase()}`}>
              {/* ── Header bar ─────────────────────────────────────── */}
              <div className="card-header-bar" onClick={() => toggleExpand(item.contradiction_id)}>
                <div className="card-header-left">
                  <span className={`sev-tag ${sevBadge}`}>{severity}</span>
                  <h3 className="field-title">{item.field.toUpperCase().replace(/_/g, ' ')}</h3>
                  <span className="comparison-tag">{item.comparison || 'MISMATCH'}</span>
                </div>
                <div className="card-header-right">
                  <span className="contradiction-id-code"><code>{item.contradiction_id}</code></span>
                  <span className="expand-toggle">{isExpanded ? '▲' : '▼'}</span>
                </div>
              </div>

              {isExpanded && (
                <div className="card-body">

                  {/* ── PROMINENT VALUE DIFF ────────────────────────── */}
                  <div className={`value-diff-banner sev-diff-${severity.toLowerCase()}`}>
                    <div className="diff-side diff-side-a">
                      <span className="diff-doc-label">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="7" y1="8" x2="17" y2="8"/></svg>
                        {item.document_a}
                      </span>
                      <span className="diff-value">{String(item.value_a)}</span>
                      {item.normalized_value_a && (
                        <span className="diff-normalized">normalized: {String(item.normalized_value_a)}</span>
                      )}
                    </div>

                    <div className="diff-center">
                      <div className={`diff-badge diff-badge-${severity.toLowerCase()}`}>≠</div>
                      <span className="diff-field-name">{item.field}</span>
                    </div>

                    <div className="diff-side diff-side-b">
                      <span className="diff-doc-label">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="7" y1="8" x2="17" y2="8"/></svg>
                        {item.document_b}
                      </span>
                      <span className="diff-value">{String(item.value_b)}</span>
                      {item.normalized_value_b && (
                        <span className="diff-normalized">normalized: {String(item.normalized_value_b)}</span>
                      )}
                    </div>
                  </div>

                  {/* ── VISUAL PROVENANCE TREE ───────────────────────── */}
                  <div className="provenance-flow-container">
                    <div className="provenance-header">
                      <span className="prov-title">Evidence Provenance Relationship</span>
                      <button
                        type="button"
                        className="btn-tree-toggle"
                        onClick={() => toggleTree(item.contradiction_id)}
                      >
                        {isTreeOpen ? 'Hide Flow' : 'Show Flow'}
                      </button>
                    </div>

                    {isTreeOpen && (
                      <div className="provenance-tree-diagram">
                        {/* Document A */}
                        <div className="tree-node node-doc node-doc-a">
                          <div className="node-badge">DOCUMENT A SOURCE</div>
                          <strong className="node-doc-id">{item.document_a}</strong>
                        </div>

                        <div className="tree-arrow down">↓</div>

                        {/* Evidence A */}
                        <div className="tree-node node-evidence node-ev-a">
                          <div className="node-header">
                            <span className="ev-badge">EVIDENCE A</span>
                            <code className="ev-id">{evA ? evA.evidence_id : (item.evidence_ids?.[0] || 'evidence.a')}</code>
                          </div>
                          <div className="node-body">
                            <div className="field-row"><small>Field:</small> <code>{item.field}</code></div>
                            <div className="val-row"><small>Value:</small> <strong className="val-text">{String(item.value_a)}</strong></div>
                            {item.normalized_value_a && (
                              <div className="norm-row"><small>Normalized:</small> <code>{String(item.normalized_value_a)}</code></div>
                            )}
                            <div className="meta-sub-row">
                              <span>Source: <em>{evA ? evA.source : 'document.field'}</em></span>
                              <span className="sep">•</span>
                              <span>Confidence: {evA?.confidence != null ? `${(evA.confidence * 100).toFixed(0)}%` : 'Unavailable'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="tree-arrow down">↓</div>

                        {/* Contradiction Center */}
                        <div className={`tree-node node-contradiction-center sev-${severity.toLowerCase()}`}>
                          <div className="contradiction-center-header">
                            <span className="lightning-icon">⚡</span>
                            <strong>{severity} CONTRADICTION ({item.comparison || 'MISMATCH'})</strong>
                          </div>
                          <div className="contradiction-center-body">
                            <span>Field: <code>{item.field}</code></span>
                            <span>ID: <code>{item.contradiction_id}</code></span>
                          </div>
                        </div>

                        <div className="tree-arrow up">↑</div>

                        {/* Evidence B */}
                        <div className="tree-node node-evidence node-ev-b">
                          <div className="node-header">
                            <span className="ev-badge">EVIDENCE B</span>
                            <code className="ev-id">{evB ? evB.evidence_id : (item.evidence_ids?.[1] || 'evidence.b')}</code>
                          </div>
                          <div className="node-body">
                            <div className="field-row"><small>Field:</small> <code>{item.field}</code></div>
                            <div className="val-row"><small>Value:</small> <strong className="val-text">{String(item.value_b)}</strong></div>
                            {item.normalized_value_b && (
                              <div className="norm-row"><small>Normalized:</small> <code>{String(item.normalized_value_b)}</code></div>
                            )}
                            <div className="meta-sub-row">
                              <span>Source: <em>{evB ? evB.source : 'document.field'}</em></span>
                              <span className="sep">•</span>
                              <span>Confidence: {evB?.confidence != null ? `${(evB.confidence * 100).toFixed(0)}%` : 'Unavailable'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="tree-arrow up">↑</div>

                        {/* Document B */}
                        <div className="tree-node node-doc node-doc-b">
                          <div className="node-badge">DOCUMENT B SOURCE</div>
                          <strong className="node-doc-id">{item.document_b}</strong>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* ── METADATA GRID ───────────────────────────────── */}
                  <div className="contradiction-meta-grid">
                    <div className="meta-item">
                      <span className="meta-lbl">Contradiction ID</span>
                      <span className="meta-val"><code>{item.contradiction_id}</code></span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-lbl">Field Examined</span>
                      <span className="meta-val"><code>{item.field}</code></span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-lbl">Comparison Status</span>
                      <span className="meta-val"><span className="comparison-tag">{item.comparison || 'MISMATCH'}</span></span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-lbl">Severity</span>
                      <span className="meta-val"><span className={`sev-tag ${sevBadge}`}>{severity}</span></span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-lbl">Source Documents</span>
                      <span className="meta-val"><code>{item.document_a}</code> vs <code>{item.document_b}</code></span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-lbl">Comparison Confidence</span>
                      <span className={`meta-val ${confidenceDisplay === 'Unavailable' ? 'null-val' : 'highlight-conf'}`}>
                        {confidenceDisplay}
                      </span>
                    </div>

                    <div className="meta-item full-width">
                      <span className="meta-lbl">Source Evidence IDs</span>
                      <div className="evidence-ids-chips">
                        {item.evidence_ids && item.evidence_ids.length > 0 ? (
                          item.evidence_ids.map(id => (
                            <button
                              key={id}
                              type="button"
                              className="evidence-id-chip"
                              onClick={() => onSelectEvidenceId && onSelectEvidenceId(id)}
                              title="View in Evidence Explorer"
                            >
                              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                              </svg>
                              {id}
                            </button>
                          ))
                        ) : (
                          <span className="muted-text">See evidence register</span>
                        )}
                      </div>
                    </div>

                    <div className="meta-item full-width">
                      <span className="meta-lbl">DAKSH Reasoning Explanation</span>
                      <p className="explanation-paragraph">{item.explanation}</p>
                    </div>
                  </div>

                  {/* ── SUPPORTING EVIDENCE RECORDS ─────────────────── */}
                  {supportingEvidenceItems.length > 0 && (
                    <div className="expandable-evidence-records">
                      <h4 className="records-title">Supporting Evidence Records ({supportingEvidenceItems.length})</h4>
                      <div className="records-grid">
                        {supportingEvidenceItems.map(ev => (
                          <div key={ev.evidence_id} className="ev-record-card">
                            <div className="rec-header">
                              <span className="source-chip">{ev.source}</span>
                              <code>{ev.evidence_id}</code>
                            </div>
                            <div className="rec-body">
                              <div><small>Field:</small> <strong>{ev.field}</strong></div>
                              <div><small>Value:</small> <code>{String(ev.value)}</code></div>
                              <div><small>Normalized:</small> <code>{ev.normalized_value != null ? String(ev.normalized_value) : '—'}</code></div>
                              <div><small>Confidence:</small> {ev.confidence != null ? `${(ev.confidence * 100).toFixed(0)}%` : 'Unavailable'}</div>
                              <div><small>Quality:</small> {ev.quality != null ? `${(ev.quality * 100).toFixed(0)}%` : 'Unavailable'}</div>
                              {ev.description && <div className="rec-desc">{ev.description}</div>}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                </div>
              )}
            </article>
          )
        })}
      </div>
    </section>
  )
}
