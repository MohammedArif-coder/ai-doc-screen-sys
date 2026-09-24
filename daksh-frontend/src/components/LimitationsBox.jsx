export function LimitationsBox({ adapterErrors, reasons }) {
  // Extract explicit limitation reasons or adapter errors
  const limitations = []

  if (adapterErrors && adapterErrors.length > 0) {
    adapterErrors.forEach(err => {
      // Clean up adapter error string to ensure clean presentation
      const cleanErr = err.replace(/:\s*adapter processing failed/i, ' analysis unavailable')
      limitations.push(cleanErr)
    })
  }

  if (reasons && reasons.length > 0) {
    reasons.forEach(r => {
      const u = r.toUpperCase()
      if (u.includes('UNAVAILABLE') || u.includes('NOT_CONFIGURED') || u.includes('LIMITATION') || u.includes('NOT_CHECKED') || u.includes('POOR QUALITY')) {
        // Sanitize string to avoid "failed" or "suspicious" words
        let cleanReason = r
          .replace(/failed/gi, 'was unavailable')
          .replace(/suspicious/gi, 'requires verification')
        if (!limitations.includes(cleanReason)) {
          limitations.push(cleanReason)
        }
      }
    })
  }

  if (limitations.length === 0) return null

  return (
    <section className="panel limitations-container">
      <div className="limitations-header">
        <div className="limitation-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" strokeWidth="2">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
        </div>
        <div>
          <span className="section-badge badge-limitation">SYSTEM LIMITATIONS</span>
          <h3>Module & Processing Limitations</h3>
        </div>
      </div>

      <ul className="limitations-list">
        {limitations.map((item, idx) => (
          <li key={idx} className="limitation-item">
            <span className="bullet-dot">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </section>
  )
}
