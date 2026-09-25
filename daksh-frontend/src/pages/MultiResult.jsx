import { useLocation, Link, Navigate } from 'react-router-dom'
import { ChevronLeft, FlaskConical, AlertOctagon, ArrowRight } from 'lucide-react'
import StatusPill from '../components/StatusPill.jsx'

function DocumentNetwork({ nodes }) {
  const cx = 260
  const cy = 150
  const radius = 100
  const positions = nodes.map((n, i) => {
    const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2
    return { ...n, x: cx + radius * Math.cos(angle), y: cy + radius * Math.sin(angle) }
  })

  return (
    <svg viewBox="0 0 520 300" className="w-full" role="img" aria-label="Document relationship network">
      {positions.map((p) => (
        <line key={p.id} x1={cx} y1={cy} x2={p.x} y2={p.y} stroke="#E3E7EE" strokeWidth="1.5" />
      ))}
      <circle cx={cx} cy={cy} r="34" fill="#0E7C7B" />
      <text x={cx} y={cy + 4} textAnchor="middle" fontSize="11" fontWeight="600" fill="#fff">
        CASE
      </text>
      {positions.map((p) => (
        <g key={p.id}>
          <circle cx={p.x} cy={p.y} r="26" fill="#FFFFFF" stroke="#2F5DA8" strokeWidth="1.5" />
          <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize="9.5" fontWeight="600" fill="#1B3B72">
            {p.label.length > 8 ? p.label.slice(0, 7) + '…' : p.label}
          </text>
        </g>
      ))}
    </svg>
  )
}

export default function MultiResult() {
  const { state } = useLocation()
  const result = state?.result

  if (!result) return <Navigate to="/multi" replace />

  const riskTone = result.overallRisk === 'high' ? 'high' : result.overallRisk === 'medium' ? 'review' : 'match'

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <Link to="/multi" className="flex items-center gap-1 text-xs font-medium text-muted hover:text-ink">
        <ChevronLeft size={14} /> New case
      </Link>

      {result.demo && (
        <div className="mt-4 inline-flex items-center gap-1.5 rounded-md bg-ink/5 px-2.5 py-1 text-[11px] font-medium text-muted">
          <FlaskConical size={12} /> Demo data — not a live engine result
        </div>
      )}

      {/* Case summary */}
      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-engine">Case Summary</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">{result.applicant}</h1>
          <p className="mt-1 text-xs text-muted tabular">Case ID: {result.caseId}</p>
        </div>
        <StatusPill tone={riskTone} label={`${result.overallRisk.toUpperCase()} RISK`} />
      </div>

      <div className="mt-5 grid grid-cols-3 gap-4">
        {[
          { label: 'Documents analyzed', value: result.documentsAnalyzed },
          { label: 'Fields compared', value: result.fieldsCompared },
          { label: 'Contradictions found', value: result.contradictionsFound }
        ].map((s) => (
          <div key={s.label} className="rounded-md border border-border bg-white px-4 py-3.5">
            <p className="text-[11px] font-medium text-muted">{s.label}</p>
            <p className="mt-1 text-lg font-semibold tabular text-ink">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Document network */}
      <section className="mt-8 rounded-lg border border-border bg-white p-6 shadow-card">
        <h2 className="text-sm font-semibold text-ink">Document Network</h2>
        <div className="mt-2 flex justify-center">
          <DocumentNetwork nodes={result.network} />
        </div>
      </section>

      {/* Cross-document comparison */}
      <section className="mt-6 rounded-lg border border-border bg-white p-6 shadow-card">
        <h2 className="text-sm font-semibold text-ink">Cross-Document Comparison</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[560px] text-sm">
            <thead>
              <tr className="border-b border-border text-left text-[11px] font-medium uppercase tracking-wide text-muted">
                <th className="py-2 pr-4">Field</th>
                {Object.keys(result.comparison[0].values).map((doc) => (
                  <th key={doc} className="py-2 pr-4 font-medium">
                    {doc}
                  </th>
                ))}
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {result.comparison.map((row) => (
                <tr key={row.field}>
                  <td className="py-2.5 pr-4 font-medium text-ink">{row.field}</td>
                  {Object.values(row.values).map((v, i) => (
                    <td key={i} className="py-2.5 pr-4 tabular text-ink/80">
                      {v}
                    </td>
                  ))}
                  <td className="py-2.5">
                    <StatusPill tone={row.status} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Contradictions */}
      <section className="mt-6">
        <h2 className="text-sm font-semibold text-ink">Contradictions</h2>
        <div className="mt-4 space-y-3">
          {result.contradictions.length === 0 && (
            <p className="text-sm text-muted">No contradictions detected across the compared fields.</p>
          )}
          {result.contradictions.map((c, i) => (
            <div key={i} className="rounded-lg border border-danger-light bg-danger-light/40 p-5">
              <div className="flex items-start gap-3">
                <AlertOctagon size={17} className="mt-0.5 shrink-0 text-danger" />
                <div className="w-full">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-semibold text-danger">{c.title}</p>
                    <StatusPill tone="high" size="sm" label={`Severity: ${c.severity.toUpperCase()}`} />
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-3">
                    <div className="rounded-md bg-white px-3 py-2.5">
                      <p className="text-[11px] text-muted">{c.sourceA.label} (Source)</p>
                      <p className="mt-0.5 text-sm font-medium text-ink">{c.sourceA.value}</p>
                    </div>
                    <div className="rounded-md bg-white px-3 py-2.5">
                      <p className="text-[11px] text-muted">{c.sourceB.label} (Source)</p>
                      <p className="mt-0.5 text-sm font-medium text-ink">{c.sourceB.value}</p>
                    </div>
                  </div>
                  <p className="mt-3 text-xs leading-relaxed text-ink/70">
                    <span className="font-medium text-ink">Why it matters: </span>
                    {c.explanation}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Evidence chain */}
      <section className="mt-6 mb-4 rounded-lg border border-border bg-white p-6 shadow-card">
        <h2 className="text-sm font-semibold text-ink">Evidence Chain</h2>
        <div className="mt-4 flex flex-wrap items-center gap-2 text-xs font-medium text-muted">
          {['Document', 'Extracted field', 'Comparison', 'Evidence', 'Finding', 'Decision'].map((step, i, arr) => (
            <span key={step} className="flex items-center gap-2">
              <span className="rounded-md border border-border bg-bg px-2.5 py-1.5 text-ink/80">{step}</span>
              {i < arr.length - 1 && <ArrowRight size={12} className="text-border" />}
            </span>
          ))}
        </div>
        <p className="mt-3 text-xs text-muted">
          Every finding above traces back through this chain — DAKSH surfaces reasoning, not just a verdict.
        </p>
      </section>
    </div>
  )
}
