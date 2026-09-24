import { useState, useMemo, useEffect, useRef } from 'react'
import { EvidenceDetailModal } from './EvidenceDetailModal'

export function EvidenceExplorer({ evidence, highlightedId }) {
  const [selectedDocFilter, setSelectedDocFilter] = useState('ALL')
  const [selectedTypeFilter, setSelectedTypeFilter] = useState('ALL')
  const [searchQuery, setSearchQuery] = useState('')
  const [inspectItem, setInspectItem] = useState(null)
  const highlightRef = useRef(null)

  // Auto-scroll to highlighted row
  useEffect(() => {
    if (highlightedId && highlightRef.current) {
      highlightRef.current.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }, [highlightedId])

  const docIds = useMemo(() => {
    if (!evidence) return []
    return ['ALL', ...new Set(evidence.map(item => item.document_id))]
  }, [evidence])

  const filteredEvidence = useMemo(() => {
    if (!evidence) return []
    return evidence.filter(item => {
      const matchDoc = selectedDocFilter === 'ALL' || item.document_id === selectedDocFilter
      const matchType = selectedTypeFilter === 'ALL' || item.evidence_type === selectedTypeFilter
      const query = searchQuery.toLowerCase().trim()
      const matchQuery = !query || (
        item.evidence_id.toLowerCase().includes(query) ||
        item.field.toLowerCase().includes(query) ||
        item.source.toLowerCase().includes(query) ||
        String(item.value).toLowerCase().includes(query) ||
        (item.description && item.description.toLowerCase().includes(query))
      )
      return matchDoc && matchType && matchQuery
    })
  }, [evidence, selectedDocFilter, selectedTypeFilter, searchQuery])

  const groupedData = useMemo(() => {
    const groups = {}
    filteredEvidence.forEach(item => {
      const doc = item.document_id
      if (!groups[doc]) groups[doc] = { OBSERVATION: [], DERIVED: [], DECISION: [] }
      const type = item.evidence_type || 'OBSERVATION'
      if (!groups[doc][type]) groups[doc][type] = []
      groups[doc][type].push(item)
    })
    return groups
  }, [filteredEvidence])

  if (!evidence || evidence.length === 0) {
    return (
      <section className="panel evidence-explorer-container">
        <div className="section-title-row">
          <div>
            <span className="section-badge">TRACEABILITY</span>
            <h2>Evidence Explorer</h2>
          </div>
        </div>
        <div className="empty-state-box">
          <p>No evidence items extracted. Run a screening case to populate the register.</p>
        </div>
      </section>
    )
  }

  return (
    <section className="panel evidence-explorer-container">
      <div className="section-title-row">
        <div>
          <span className="section-badge">FORENSIC TRACEABILITY</span>
          <h2>Evidence Explorer & Register</h2>
          <p className="section-sub">Normalized observations, derivations, and source provenance across analyzed documents.</p>
        </div>
        <span className="count-pill">{filteredEvidence.length} Items</span>
      </div>

      {/* Filter / Search Toolbar */}
      <div className="explorer-toolbar">
        <div className="search-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2">
            <circle cx="11" cy="11" r="8"/>
            <line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            type="text"
            placeholder="Search field, value, ID or source..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          {searchQuery && (
            <button className="clear-search" onClick={() => setSearchQuery('')}>✕</button>
          )}
        </div>

        {/* Chip-style document filter */}
        <div className="filter-chips-group">
          {docIds.map(doc => (
            <button
              key={doc}
              type="button"
              className={`filter-chip ${selectedDocFilter === doc ? 'chip-active' : ''}`}
              onClick={() => setSelectedDocFilter(doc)}
            >
              {doc === 'ALL' ? 'All Docs' : doc.replace(/-demo-\d+/, '').toUpperCase()}
            </button>
          ))}
        </div>

        {/* Chip-style type filter */}
        <div className="filter-chips-group">
          {[['ALL', 'All Types'], ['OBSERVATION', 'Observations'], ['DERIVED', 'Derived']].map(([val, lbl]) => (
            <button
              key={val}
              type="button"
              className={`filter-chip ${selectedTypeFilter === val ? 'chip-active' : ''}`}
              onClick={() => setSelectedTypeFilter(val)}
            >
              {lbl}
            </button>
          ))}
        </div>
      </div>

      {/* Evidence Groups */}
      <div className="evidence-groups-wrapper">
        {Object.keys(groupedData).length === 0 ? (
          <div className="empty-search-results">
            <p>No evidence items match "{searchQuery}".</p>
          </div>
        ) : (
          Object.entries(groupedData).map(([docId, types]) => {
            const hasObservations = types.OBSERVATION.length > 0
            const hasDerived = types.DERIVED.length > 0 || types.DECISION.length > 0

            return (
              <div key={docId} className="doc-evidence-group">
                <div className="group-doc-header">
                  <div className="doc-header-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" strokeWidth="2">
                      <rect x="3" y="4" width="18" height="16" rx="2"/>
                      <line x1="7" y1="8" x2="17" y2="8"/>
                      <line x1="7" y1="12" x2="17" y2="12"/>
                    </svg>
                    <h3>{docId}</h3>
                  </div>
                  <span className="group-count">
                    {types.OBSERVATION.length + types.DERIVED.length + types.DECISION.length} items
                  </span>
                </div>

                {hasObservations && (
                  <div className="subcategory-block">
                    <h4 className="subcat-title">
                      <span className="type-badge badge-obs">OBSERVATIONS</span>
                      <small>Raw extracted fields from document intake</small>
                    </h4>
                    <EvidenceTable
                      items={types.OBSERVATION}
                      highlightedId={highlightedId}
                      highlightRef={highlightRef}
                      onInspect={(item) => setInspectItem(item)}
                    />
                  </div>
                )}

                {hasDerived && (
                  <div className="subcategory-block">
                    <h4 className="subcat-title">
                      <span className="type-badge badge-derived">DERIVED EVIDENCE</span>
                      <small>Cross-field derivations, QR checks, and decision logic</small>
                    </h4>
                    <EvidenceTable
                      items={[...types.DERIVED, ...types.DECISION]}
                      highlightedId={highlightedId}
                      highlightRef={highlightRef}
                      onInspect={(item) => setInspectItem(item)}
                    />
                  </div>
                )}
              </div>
            )
          })
        )}
      </div>

      {inspectItem && (
        <EvidenceDetailModal item={inspectItem} onClose={() => setInspectItem(null)} />
      )}
    </section>
  )
}

function EvidenceTable({ items, highlightedId, highlightRef, onInspect }) {
  return (
    <div className="table-scroll-wrapper">
      <table className="evidence-table">
        <thead>
          <tr>
            <th>Evidence ID</th>
            <th>Source</th>
            <th>Field</th>
            <th>Value</th>
            <th>Confidence</th>
            <th>Quality</th>
            <th>Severity</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => {
            const isHighlighted = highlightedId === item.evidence_id
            const confidenceText = (item.confidence === null || item.confidence === undefined)
              ? 'Unavailable'
              : `${(item.confidence * 100).toFixed(0)}%`
            const qualityText = (item.quality === null || item.quality === undefined)
              ? 'Unavailable'
              : `${(item.quality * 100).toFixed(0)}%`

            return (
              <tr
                key={item.evidence_id}
                ref={isHighlighted ? highlightRef : null}
                className={`table-row ${isHighlighted ? 'row-highlighted' : ''}`}
              >
                <td className="cell-id"><code>{item.evidence_id}</code></td>
                <td><span className="source-chip">{item.source}</span></td>
                <td className="cell-field">{item.field}</td>
                <td className="cell-value" title={String(item.value)}>
                  {typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value)}
                </td>
                <td className={`cell-conf ${confidenceText === 'Unavailable' ? 'conf-null' : ''}`}>
                  {confidenceText}
                </td>
                <td className={`cell-qual ${qualityText === 'Unavailable' ? 'qual-null' : ''}`}>
                  {qualityText}
                </td>
                <td>
                  {item.severity ? (
                    <span className={`sev-tag-sm sev-${item.severity.toLowerCase()}`}>
                      {item.severity}
                    </span>
                  ) : (
                    <span className="muted-dash">—</span>
                  )}
                </td>
                <td>
                  <button
                    type="button"
                    className="btn-inspect-sm"
                    onClick={() => onInspect(item)}
                  >
                    Inspect
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
