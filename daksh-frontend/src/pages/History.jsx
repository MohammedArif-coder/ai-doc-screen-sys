import { FlaskConical } from 'lucide-react'
import { DEMO_CASES } from '../api/multiDocumentApi.js'
import StatusPill from '../components/StatusPill.jsx'

const RISK_TONE = { low: 'match', medium: 'review', high: 'high' }

export default function History() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <p className="text-sm font-medium text-brand-500">History</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">Cases</h1>
      <p className="mt-2 text-sm text-muted">
        No persistent case store is connected in this environment. The cases below are illustrative
        demo cases for presentation purposes.
      </p>

      <div className="mt-6 inline-flex items-center gap-1.5 rounded-md bg-ink/5 px-2.5 py-1 text-[11px] font-medium text-muted">
        <FlaskConical size={12} /> Demo data
      </div>

      <div className="mt-4 divide-y divide-border rounded-lg border border-border bg-white shadow-card">
        {DEMO_CASES.map((c) => (
          <div key={c.id} className="flex items-center justify-between px-6 py-4">
            <div>
              <p className="text-sm font-medium text-ink">{c.title}</p>
              <p className="text-xs text-muted">{c.description}</p>
            </div>
            <StatusPill tone={RISK_TONE[c.risk]} label={`${c.risk.toUpperCase()} RISK`} size="sm" />
          </div>
        ))}
      </div>
    </div>
  )
}
