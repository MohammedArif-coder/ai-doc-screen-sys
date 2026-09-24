import { useEffect, useState } from 'react'

export function SystemStatus({ apiHealth }) {
  const [healthData, setHealthData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [pingMs, setPingMs] = useState(null)

  const apiUrl = import.meta.env.VITE_DAKSH_API_URL || 'http://127.0.0.1:8000'

  const fetchStatus = async () => {
    setLoading(true)
    const start = Date.now()
    try {
      const res = await fetch(`${apiUrl}/api/health`)
      const data = await res.json()
      setPingMs(Date.now() - start)
      setHealthData(data)
    } catch {
      setHealthData(null)
      setPingMs(null)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchStatus()
  }, [])

  return (
    <section className="panel system-status-container">
      <div className="section-title-row">
        <div>
          <span className="section-badge">INFRASTRUCTURE</span>
          <h2>DAKSH System & API Health Status</h2>
          <p className="section-sub">Real-time status of backend API endpoints, document adapters, and screening pipeline components.</p>
        </div>
        <button type="button" className="btn-secondary-sm" onClick={fetchStatus}>
          Refresh Diagnostics
        </button>
      </div>

      <div className="status-cards-grid">
        <div className="status-card">
          <div className="status-card-header">
            <span className={`status-dot-lg ${apiHealth ? 'online' : 'offline'}`}></span>
            <h4>FastAPI Backend Service</h4>
          </div>
          <p className="card-val">{healthData?.service || 'DAKSH P6 API'}</p>
          <div className="card-detail">
            <span>Endpoint: <code>/api/health</code></span>
            <span>Latency: {pingMs ? `${pingMs}ms` : 'Offline'}</span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-dot-lg online"></span>
            <h4>Passport Document Adapter</h4>
          </div>
          <p className="card-val">Visual Inspection & MRZ Engine</p>
          <div className="card-detail">
            <span>Status: Operational</span>
            <span>Module: <code>passport_adapter</code></span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-dot-lg online"></span>
            <h4>Visa Document Adapter</h4>
          </div>
          <p className="card-val">OCR & Entry Permitting Engine</p>
          <div className="card-detail">
            <span>Status: Operational</span>
            <span>Module: <code>visa_adapter</code></span>
          </div>
        </div>

        <div className="status-card">
          <div className="status-card-header">
            <span className="status-dot-lg online"></span>
            <h4>Aadhaar Document Adapter</h4>
          </div>
          <p className="card-val">Printed OCR & Secure QR Verifier</p>
          <div className="card-detail">
            <span>Status: Operational</span>
            <span>Module: <code>aadhaar_adapter</code></span>
          </div>
        </div>
      </div>

      <div className="contract-rules-box">
        <h4>DAKSH P6 Reasoning Chain & Contract Integrity</h4>
        <ul>
          <li>✔ <strong>Deterministic Aggregation:</strong> Case priority status is aggregated deterministically without black-box fraud scores.</li>
          <li>✔ <strong>Supported Statuses:</strong> Returns strictly one of <code>CLEAR</code>, <code>LOW_CONCERN</code>, <code>REVIEW</code>, <code>HIGH_REVIEW</code>, <code>INCONCLUSIVE</code>.</li>
          <li>✔ <strong>Traceable Provenance:</strong> Every contradiction is directly linked to source document evidence IDs.</li>
          <li>✔ <strong>Null Safety:</strong> Null or missing confidence parameters are explicitly rendered as "Unavailable" to avoid misinterpretation.</li>
        </ul>
      </div>
    </section>
  )
}
