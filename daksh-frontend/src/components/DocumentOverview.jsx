const DOC_SVG_ICONS = {
  Passport: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#38BDF8" strokeWidth="1.8">
      <rect x="4" y="2" width="16" height="20" rx="2"/>
      <line x1="8" y1="6" x2="16" y2="6"/>
      <line x1="8" y1="10" x2="16" y2="10"/>
      <circle cx="12" cy="15.5" r="2"/>
    </svg>
  ),
  Visa: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#A5B4FC" strokeWidth="1.8">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  ),
  Aadhaar: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#34D399" strokeWidth="1.8">
      <rect x="3" y="4" width="18" height="16" rx="2"/>
      <circle cx="9" cy="10.5" r="2.5"/>
      <path d="M15 8h2M15 12h2M7 16h10"/>
    </svg>
  ),
  'Driving Licence': (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="1.8">
      <rect x="3" y="4" width="18" height="16" rx="2"/>
      <path d="M7 15h10M7 9h4"/>
    </svg>
  ),
  PAN: (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#EC4899" strokeWidth="1.8">
      <rect x="3" y="4" width="18" height="16" rx="2"/>
      <line x1="7" y1="8" x2="17" y2="8"/>
      <line x1="7" y1="12" x2="13" y2="12"/>
    </svg>
  )
}

export function DocumentOverview({ documents, evidence, adapterErrors, files }) {
  const docTypes = [
    { key: 'Passport', label: 'Passport' },
    { key: 'Visa', label: 'Visa' },
    { key: 'Aadhaar', label: 'Aadhaar' },
    { key: 'Driving Licence', label: 'Driving Licence' },
    { key: 'PAN', label: 'PAN Card' }
  ]

  return (
    <section className="panel doc-overview-container">
      <div className="section-title-row">
        <div>
          <span className="section-badge">CASE INPUTS</span>
          <h2>Document Intake Overview</h2>
          <p className="section-sub">Individual document module status and extracted evidence yield.</p>
        </div>
        <span className="count-pill">{documents?.length || 0} Ingested</span>
      </div>

      <div className="doc-cards-grid">
        {docTypes.map(({ key, label }) => {
          const doc = documents?.find(d => d.document_type.toLowerCase() === key.toLowerCase())
          const fileKey = key.toLowerCase() === 'driving licence' ? 'driving_licence' : key.toLowerCase()
          const fileObj = files?.[fileKey]
          const docEvCount = evidence?.filter(e => doc && e.document_id === doc.document_id).length || 0
          const moduleError = adapterErrors?.find(err => err.toLowerCase().includes(fileKey.toLowerCase()))

          let status = doc ? (doc.processing_status || 'completed') : 'unavailable'
          if (moduleError) status = 'failed'

          const statusLabel = {
            completed: '✓ Completed',
            failed: '✕ Failed',
            unavailable: 'Not Submitted',
            partial: '⚡ Partial'
          }[status] || status

          return (
            <article key={key} className={`doc-summary-card status-${status}`}>
              {/* Header row: icon + status */}
              <div className="doc-card-header">
                <div className="doc-icon-svg">
                  {DOC_SVG_ICONS[key]}
                </div>
                <span className={`status-badge-sm badge-${status}`}>{statusLabel}</span>
              </div>

              {/* Document type title + ID */}
              <h3 className="doc-card-title">{label}</h3>
              <p className="doc-id-label">{doc ? doc.document_id : '— not uploaded'}</p>

              {/* Preview thumbnail — full width if available */}
              {fileObj?.previewUrl && (
                <div className="doc-preview-thumb-full">
                  <img src={fileObj.previewUrl} alt={label} />
                  <div className="thumb-filename">{fileObj.name}</div>
                </div>
              )}

              {/* Module error */}
              {moduleError && (
                <div className="module-error-box">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#F43F5E" strokeWidth="2">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                  </svg>
                  <span>{label} analysis unavailable</span>
                </div>
              )}

              {/* Footer: evidence count + status bar */}
              <div className="doc-card-footer">
                <span className="ev-count"><strong>{docEvCount}</strong> evidence items</span>
                <div className={`doc-status-bar bar-${status}`}></div>
              </div>
            </article>
          )
        })}
      </div>
    </section>
  )
}
