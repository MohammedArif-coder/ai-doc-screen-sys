import { ShieldCheck, Circle } from 'lucide-react'
import { MODULES, MULTI_DOC_ENGINE, MODULE_STATUS } from '../config/modules.js'

function overallCoreStatus() {
  const anyOnline = MODULES.some((m) => m.status === MODULE_STATUS.ONLINE)
  return anyOnline ? MODULE_STATUS.ONLINE : MODULE_STATUS.NOT_CONNECTED
}

export default function Header() {
  const core = overallCoreStatus()
  const isOnline = core === MODULE_STATUS.ONLINE

  return (
    <header className="sticky top-0 z-30 border-b border-border bg-white/90 backdrop-blur">
      <div className="flex h-16 items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-900 text-white">
            <ShieldCheck size={18} strokeWidth={2.25} />
          </div>
          <div className="leading-tight">
            <p className="text-[15px] font-semibold tracking-tight text-ink">DAKSH</p>
            <p className="text-[11px] text-muted">Document Intelligence &amp; Verification</p>
          </div>
        </div>

        <div className="hidden items-center gap-6 md:flex">
          <div className="flex items-center gap-2 text-xs text-muted">
            <Circle
              size={8}
              className={isOnline ? 'fill-success text-success' : 'fill-muted text-muted'}
            />
            <span className="tabular">
              CORE ENGINE&nbsp;
              <span className={isOnline ? 'text-success font-medium' : 'text-muted font-medium'}>
                {isOnline ? 'ONLINE' : 'NOT CONNECTED'}
              </span>
            </span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="text-xs text-muted tabular">
            MODULES&nbsp;
            <span className="font-medium text-ink">
              {MODULES.filter((m) => m.status === MODULE_STATUS.ONLINE).length}/{MODULES.length} live
            </span>
          </div>
          <div className="h-4 w-px bg-border" />
          <div className="text-xs text-muted tabular">
            ANALYSIS ENGINE&nbsp;
            <span
              className={
                MULTI_DOC_ENGINE.status === MODULE_STATUS.ONLINE
                  ? 'font-medium text-success'
                  : 'font-medium text-muted'
              }
            >
              {MULTI_DOC_ENGINE.status === MODULE_STATUS.ONLINE ? 'READY' : 'MOCK MODE'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden h-8 w-8 items-center justify-center rounded-full bg-brand-100 text-xs font-semibold text-brand-700 sm:flex">
            OV
          </div>
        </div>
      </div>
    </header>
  )
}
