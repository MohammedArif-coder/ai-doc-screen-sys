import { useEffect, useState } from 'react'

export function Navbar({ activeTab, setActiveTab, apiHealth, onResetCase }) {
  const [latency, setLatency] = useState(null)

  useEffect(() => {
    let active = true
    const checkPing = async () => {
      const start = Date.now()
      try {
        const res = await fetch(`${import.meta.env.VITE_DAKSH_API_URL || 'http://127.0.0.1:8000'}/api/health`)
        if (res.ok && active) {
          setLatency(Date.now() - start)
        }
      } catch {
        if (active) setLatency(null)
      }
    }
    checkPing()
    const interval = setInterval(checkPing, 10000)
    return () => {
      active = false
      clearInterval(interval)
    }
  }, [])

  return (
    <header className="navbar">
      <div className="navbar-brand" onClick={onResetCase} style={{ cursor: 'pointer' }}>
        <div className="brand-logo">
          <svg width="22" height="24" viewBox="0 0 24 26" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1L2 5V12C2 18.5 6.3 24.5 12 26C17.7 24.5 22 18.5 22 12V5L12 1Z" fill="#0F172A" stroke="#38BDF8" strokeWidth="2" strokeLinejoin="round"/>
            <path d="M9 12L11 14L15 10" stroke="#38BDF8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </div>
        <div className="brand-text">
          <div className="brand-name">
            DAKSH <span className="version-tag">P6</span>
          </div>
          <div className="brand-sub">Document Authentication & Knowledge-based Screening Hub</div>
        </div>
      </div>

      <nav className="navbar-nav">
        <button
          className={`nav-item ${activeTab === 'analysis' ? 'active' : ''}`}
          onClick={() => setActiveTab('analysis')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="3" width="7" height="7" rx="1"/>
            <rect x="14" y="14" width="7" height="7" rx="1"/>
            <rect x="3" y="14" width="7" height="7" rx="1"/>
          </svg>
          Case Analysis
        </button>

        <button
          className={`nav-item ${activeTab === 'evidence' ? 'active' : ''}`}
          onClick={() => setActiveTab('evidence')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
          Evidence
        </button>

        <button
          className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          History
        </button>

        <button
          className={`nav-item ${activeTab === 'status' ? 'active' : ''}`}
          onClick={() => setActiveTab('status')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          System Status
        </button>
      </nav>

      <div className="navbar-right">
        <div className={`status-pill ${apiHealth ? 'online' : 'offline'}`}>
          <span className="status-dot"></span>
          <span className="status-label">{apiHealth ? 'DAKSH Engine Online' : 'API Connecting...'}</span>
          {latency && <span className="status-ms">{latency}ms</span>}
        </div>
      </div>
    </header>
  )
}
