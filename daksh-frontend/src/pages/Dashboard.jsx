import { Link } from 'react-router-dom'
import { ScanSearch, Network, ArrowRight, FileCheck2, Layers } from 'lucide-react'
import { MODULES, MODULE_STATUS } from '../config/modules.js'

export default function Dashboard() {
  const liveModules = MODULES.filter((m) => m.status === MODULE_STATUS.ONLINE).length

  return (
    <div className="mx-auto max-w-6xl px-6 py-10">
      {/* Hero */}
      <section className="mb-12">
        <p className="text-sm font-medium text-brand-500">Document Intelligence Platform</p>
        <h1 className="mt-2 max-w-2xl text-3xl font-semibold tracking-tight text-ink sm:text-[2.25rem]">
          Verify one document, or correlate several to see the full picture.
        </h1>
        <p className="mt-3 max-w-xl text-[15px] leading-relaxed text-muted">
          DAKSH routes each document to its specialised screening module, then — when a case needs
          more than one document — links the results together to surface inconsistencies a single
          check would miss.
        </p>
      </section>

      {/* Two primary workflow cards */}
      <section className="grid gap-5 md:grid-cols-2">
        <Link
          to="/individual"
          className="group relative overflow-hidden rounded-lg border border-border bg-white p-7 shadow-card transition-all hover:-translate-y-0.5 hover:shadow-raised"
        >
          <div className="flex items-start justify-between">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-brand-50 text-brand-700">
              <ScanSearch size={22} strokeWidth={2} />
            </div>
            <span className="rounded-full bg-ink/5 px-2.5 py-1 text-[11px] font-medium text-muted tabular">
              {liveModules}/{MODULES.length} modules live
            </span>
          </div>
          <h2 className="mt-5 text-lg font-semibold text-ink">Individual Verification</h2>
          <p className="mt-2 text-sm leading-relaxed text-muted">
            Screen a single document through its dedicated module — OCR, field validation, and
            forensic checks tailored to that document type.
          </p>
          <div className="mt-5 flex flex-wrap gap-1.5">
            {MODULES.map((m) => (
              <span
                key={m.id}
                className="rounded-md border border-border bg-bg px-2 py-1 text-[11px] font-medium text-muted"
              >
                {m.shortName}
              </span>
            ))}
          </div>
          <div className="mt-7 flex items-center gap-2 text-sm font-medium text-brand-700">
            Start Individual Verification
            <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />
          </div>
        </Link>

        <Link
          to="/multi"
          className="group relative overflow-hidden rounded-lg border border-engine/30 bg-gradient-to-b from-engine-light/60 to-white p-7 shadow-card transition-all hover:-translate-y-0.5 hover:shadow-raised"
        >
          <div className="flex items-start justify-between">
            <div className="flex h-11 w-11 items-center justify-center rounded-md bg-engine text-white">
              <Network size={22} strokeWidth={2} />
            </div>
            <span className="rounded-full bg-engine/10 px-2.5 py-1 text-[11px] font-medium text-engine">
              Flagship
            </span>
          </div>
          <h2 className="mt-5 text-lg font-semibold text-ink">Multi-Document Verification</h2>
          <p className="mt-2 text-sm leading-relaxed text-muted">
            Add every document tied to one case. DAKSH links their individual results, compares
            shared fields, and flags contradictions across the set.
          </p>
          <div className="mt-5 flex items-center gap-1.5 text-[11px] font-medium text-muted">
            <span className="rounded-md border border-border bg-white px-2 py-1">Extract</span>
            <ArrowRight size={11} className="text-border" />
            <span className="rounded-md border border-border bg-white px-2 py-1">Compare</span>
            <ArrowRight size={11} className="text-border" />
            <span className="rounded-md border border-border bg-white px-2 py-1">Correlate</span>
            <ArrowRight size={11} className="text-border" />
            <span className="rounded-md border border-border bg-white px-2 py-1">Decide</span>
          </div>
          <div className="mt-7 flex items-center gap-2 text-sm font-medium text-engine">
            Start Multi-Document Verification
            <ArrowRight size={15} className="transition-transform group-hover:translate-x-0.5" />
          </div>
        </Link>
      </section>

      {/* Quick stats strip */}
      <section className="mt-6 grid grid-cols-2 gap-5 sm:grid-cols-4">
        {[
          { label: 'Modules registered', value: MODULES.length, icon: Layers },
          { label: 'Modules live', value: liveModules, icon: FileCheck2 },
          { label: 'Formats supported', value: 'JPG · PNG · PDF', icon: FileCheck2 },
          { label: 'Engine mode', value: 'Demo', icon: Network }
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-md border border-border bg-white px-4 py-3.5">
            <div className="flex items-center gap-2 text-muted">
              <Icon size={14} />
              <span className="text-[11px] font-medium">{label}</span>
            </div>
            <p className="mt-1.5 text-lg font-semibold text-ink tabular">{value}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
