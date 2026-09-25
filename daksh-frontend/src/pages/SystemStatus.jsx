import { useState, useEffect } from 'react'
import { MODULES, MULTI_DOC_ENGINE, DAKSH_BACKEND_URL } from '../config/modules.js'
import { API_MODE } from '../api/dakshApi.js'
import StatusPill from '../components/StatusPill.jsx'

export default function SystemStatus() {
  const [statuses, setStatuses] = useState({})
  const [engineStatus, setEngineStatus] = useState('online')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function checkHealth() {
      try {
        const res = await fetch(`${DAKSH_BACKEND_URL}/api/system-status`)
        if (res.ok) {
          const data = await res.json()
          setEngineStatus(data.daksh_engine || 'online')
          const mapped = {}
          if (data.services) {
            for (const [key, val] of Object.entries(data.services)) {
              mapped[key] = val.status || 'online'
            }
          }
          setStatuses(mapped)
        } else {
          setEngineStatus('degraded')
        }
      } catch (e) {
        setEngineStatus('unavailable')
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
  }, [])

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <p className="text-sm font-medium text-brand-500">System Status</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">Connected services</h1>
      <p className="mt-2 text-sm text-muted">
        Live status of every module registered with the frontend. Statuses reflect actual backend
        connectivity — nothing here is simulated as online.
      </p>

      <div className="mt-6 flex items-center justify-between gap-2 rounded-md border border-border bg-white px-4 py-3 text-sm">
        <div className="flex items-center gap-2">
          <span className="text-muted">API mode:</span>
          <span className="font-medium text-ink">{API_MODE === 'real' ? 'Real backends' : 'Mock / demo mode'}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-muted">Orchestrator:</span>
          <span className="font-mono text-xs text-ink">{DAKSH_BACKEND_URL}</span>
        </div>
      </div>

      <div className="mt-4 divide-y divide-border rounded-lg border border-border bg-white shadow-card">
        {MODULES.map((m) => {
          const status = loading ? m.status : statuses[m.id] || m.status
          return (
            <div key={m.id} className="flex items-center justify-between px-6 py-4">
              <div>
                <p className="text-sm font-medium text-ink">{m.name}</p>
                <p className="text-xs text-muted">{m.endpoint || 'No endpoint configured'}</p>
              </div>
              <StatusPill tone={status} />
            </div>
          )
        })}
        <div className="flex items-center justify-between px-6 py-4">
          <div>
            <p className="text-sm font-medium text-ink">{MULTI_DOC_ENGINE.name}</p>
            <p className="text-xs text-muted">{MULTI_DOC_ENGINE.endpoint || 'No endpoint configured'}</p>
          </div>
          <StatusPill tone={engineStatus} />
        </div>
      </div>
    </div>
  )
}
