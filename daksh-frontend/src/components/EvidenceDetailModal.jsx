export function EvidenceDetailModal({ item, onClose }) {
  if (!item) return null

  const confidenceDisplay = (item.confidence === null || item.confidence === undefined)
    ? 'Unavailable'
    : `${(item.confidence * 100).toFixed(1)}%`

  const qualityDisplay = (item.quality === null || item.quality === undefined)
    ? 'Unavailable'
    : `${(item.quality * 100).toFixed(1)}%`

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-dialog panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <div>
            <span className="section-badge">EVIDENCE RECORD INSPECTOR</span>
            <h3 className="modal-title">{item.evidence_id}</h3>
          </div>
          <button type="button" className="btn-close-modal" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          <div className="modal-grid">
            <div className="grid-item">
              <span className="lbl">Document ID</span>
              <strong className="val">{item.document_id}</strong>
            </div>

            <div className="grid-item">
              <span className="lbl">Evidence Type</span>
              <span className="val"><span className="type-badge">{item.evidence_type}</span></span>
            </div>

            <div className="grid-item">
              <span className="lbl">Source Path</span>
              <span className="val"><span className="source-chip">{item.source}</span></span>
            </div>

            <div className="grid-item">
              <span className="lbl">Field Name</span>
              <strong className="val"><code>{item.field}</code></strong>
            </div>

            <div className="grid-item full">
              <span className="lbl">Raw Extracted Value</span>
              <div className="value-box-modal">
                {typeof item.value === 'object' ? JSON.stringify(item.value, null, 2) : String(item.value)}
              </div>
            </div>

            <div className="grid-item full">
              <span className="lbl">Normalized Value</span>
              <div className="value-box-modal normalized">
                {item.normalized_value != null ? (
                  typeof item.normalized_value === 'object' ? JSON.stringify(item.normalized_value, null, 2) : String(item.normalized_value)
                ) : (
                  <span className="muted-text">None / Not Normalized</span>
                )}
              </div>
            </div>

            <div className="grid-item">
              <span className="lbl">Extraction Confidence</span>
              <span className={`val-conf ${confidenceDisplay === 'Unavailable' ? 'null-val' : ''}`}>
                {confidenceDisplay}
              </span>
            </div>

            <div className="grid-item">
              <span className="lbl">Document Quality Score</span>
              <span className={`val-qual ${qualityDisplay === 'Unavailable' ? 'null-val' : ''}`}>
                {qualityDisplay}
              </span>
            </div>

            <div className="grid-item">
              <span className="lbl">Severity Level</span>
              <span className="val">
                {item.severity ? (
                  <span className={`sev-tag-sm sev-${item.severity.toLowerCase()}`}>
                    {item.severity}
                  </span>
                ) : (
                  <span className="muted-text">None</span>
                )}
              </span>
            </div>

            <div className="grid-item full">
              <span className="lbl">Field Description & Notes</span>
              <p className="desc-text">{item.description || 'No detailed description attached to this evidence item.'}</p>
            </div>

            {item.region && (
              <div className="grid-item full">
                <span className="lbl">Document Region Bounding Box</span>
                <pre className="json-box">{JSON.stringify(item.region, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>

        <div className="modal-footer">
          <button type="button" className="btn-secondary" onClick={onClose}>Close Inspector</button>
        </div>
      </div>
    </div>
  )
}
