import { Link } from 'react-router-dom'
import { Contact, CreditCard, Car, BookUser, Stamp, ArrowRight } from 'lucide-react'
import { MODULES, MODULE_STATUS } from '../config/modules.js'
import StatusPill from '../components/StatusPill.jsx'

const ICONS = { IdCard: Contact, CreditCard, Car, BookUser, StampIcon: Stamp }

export default function IndividualSelect() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      <p className="text-sm font-medium text-brand-500">Individual Verification</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">Select a document</h1>
      <p className="mt-2 max-w-xl text-sm text-muted">
        Each document is routed to its dedicated screening module. Choose the type you want to
        verify to continue.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {MODULES.map((m) => {
          const Icon = ICONS[m.icon]
          const disabled = m.status === MODULE_STATUS.UNAVAILABLE
          const card = (
            <div
              className={`group h-full rounded-lg border border-border bg-white p-5 shadow-card transition-all ${
                disabled ? 'opacity-50' : 'hover:-translate-y-0.5 hover:shadow-raised'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-50 text-brand-700">
                  <Icon size={19} strokeWidth={2} />
                </div>
                <StatusPill tone={m.status} size="sm" />
              </div>
              <h3 className="mt-4 text-[15px] font-semibold text-ink">{m.name}</h3>
              <p className="mt-1.5 text-[13px] leading-relaxed text-muted">{m.description}</p>
              <div className="mt-4 flex flex-wrap gap-1.5">
                {m.capabilities.slice(0, 3).map((c) => (
                  <span key={c} className="rounded-md bg-ink/[0.04] px-2 py-0.5 text-[11px] text-muted">
                    {c}
                  </span>
                ))}
              </div>
              <div className="mt-4 flex items-center justify-between border-t border-border pt-3">
                <span className="text-[11px] text-muted">{m.supportedFormats.join(' · ')}</span>
                {!disabled && (
                  <span className="flex items-center gap-1 text-xs font-medium text-brand-700">
                    Select
                    <ArrowRight size={13} className="transition-transform group-hover:translate-x-0.5" />
                  </span>
                )}
              </div>
            </div>
          )
          return disabled ? (
            <div key={m.id}>{card}</div>
          ) : (
            <Link key={m.id} to={`/individual/${m.id}/upload`}>
              {card}
            </Link>
          )
        })}
      </div>
    </div>
  )
}
