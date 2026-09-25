import { useLocation, useParams, Link } from 'react-router-dom'
import { ChevronLeft, CheckCircle2, AlertTriangle, XCircle, FlaskConical } from 'lucide-react'
import { getModule } from '../config/modules.js'
import StatusPill from '../components/StatusPill.jsx'

const OUTCOME_TONE = { verified: 'verified', review: 'review', needs_review: 'needs_review', failed: 'failed' }
const CHECK_ICON = { pass: CheckCircle2, warn: AlertTriangle, fail: XCircle }
const CHECK_TONE = { pass: 'text-success', warn: 'text-warning', fail: 'text-danger' }

export default function IndividualResult() {
  const { moduleId } = useParams()
  const { state } = useLocation()
  const mod = getModule(moduleId)
  const result = state?.result

  if (!mod || !result) {
    return (
      <div className="mx-auto max-w-xl px-6 py-14 text-center">
        <p className="text-sm text-muted">
          No result to display — start a new verification from document selection.
        </p>
        <Link to="/individual" className="mt-3 inline-block text-sm font-medium text-brand-700">
          Back to Individual Verification
        </Link>
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-10">
      <Link to="/individual" className="flex items-center gap-1 text-xs font-medium text-muted hover:text-ink">
        <ChevronLeft size={14} /> New verification
      </Link>

      {result.demo && (
        <div className="mt-4 inline-flex items-center gap-1.5 rounded-md bg-ink/5 px-2.5 py-1 text-[11px] font-medium text-muted">
          <FlaskConical size={12} /> Demo data — not a live backend result
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-brand-500">Document Result</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">{mod.name}</h1>
        </div>
        <StatusPill tone={OUTCOME_TONE[result.outcome] || 'info'} />
      </div>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-6">
          {/* Identity information */}
          <section className="rounded-lg border border-border bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-ink">Identity Information</h2>
            <dl className="mt-4 divide-y divide-border">
              {result.fields.map((f) => (
                <div key={f.label} className="flex items-center justify-between py-2.5 text-sm">
                  <dt className="text-muted">{f.label}</dt>
                  <dd className="flex items-center gap-3">
                    <span className="font-medium text-ink">{f.value}</span>
                    <span className="tabular text-[11px] text-muted">{Math.round(f.confidence * 100)}%</span>
                  </dd>
                </div>
              ))}
            </dl>
          </section>

          {/* Validation checks */}
          <section className="rounded-lg border border-border bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-ink">Validation &amp; Forensics</h2>
            <ul className="mt-4 space-y-3">
              {result.checks.map((c) => {
                const Icon = CHECK_ICON[c.status] || CheckCircle2
                return (
                  <li key={c.label} className="flex gap-3">
                    <Icon size={17} className={`mt-0.5 shrink-0 ${CHECK_TONE[c.status]}`} />
                    <div>
                      <p className="text-sm font-medium text-ink">{c.label}</p>
                      <p className="text-xs text-muted">{c.detail}</p>
                    </div>
                  </li>
                )
              })}
            </ul>
          </section>

          {/* Key findings */}
          <section className="rounded-lg border border-border bg-white p-6 shadow-card">
            <h2 className="text-sm font-semibold text-ink">Key Findings</h2>
            <ul className="mt-4 space-y-2">
              {result.findings.map((f, i) => (
                <li key={i} className="rounded-md bg-bg px-4 py-3 text-sm text-ink">
                  {f}
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* Side summary */}
        <aside className="space-y-4">
          <div className="rounded-lg border border-border bg-white p-5 shadow-card">
            <p className="text-[11px] font-medium text-muted">Overall Confidence</p>
            <p className="mt-1 text-2xl font-semibold tabular text-ink">
              {Math.round(result.confidence * 100)}%
            </p>
            <div className="mt-3 h-1.5 w-full rounded-full bg-border">
              <div
                className="h-1.5 rounded-full bg-brand-500"
                style={{ width: `${Math.round(result.confidence * 100)}%` }}
              />
            </div>
          </div>
          <div className="rounded-lg border border-border bg-white p-5 shadow-card text-sm">
            <p className="text-[11px] font-medium text-muted">Module</p>
            <p className="mt-1 font-medium text-ink">{mod.name}</p>
            <p className="mt-3 text-[11px] font-medium text-muted">Capabilities used</p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {mod.capabilities.map((c) => (
                <span key={c} className="rounded-md bg-ink/[0.04] px-2 py-0.5 text-[11px] text-muted">
                  {c}
                </span>
              ))}
            </div>
          </div>
        </aside>
      </div>
    </div>
  )
}
