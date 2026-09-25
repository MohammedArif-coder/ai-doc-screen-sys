import { Check } from 'lucide-react'

/**
 * steps: [{ id, label }]
 * currentId: id of the step in progress (or null once complete)
 * doneIds: Set/array of completed step ids
 */
export default function PipelineSteps({ steps, currentId, doneIds = [] }) {
  const done = new Set(doneIds)
  return (
    <ol className="space-y-0">
      {steps.map((step, i) => {
        const isDone = done.has(step.id)
        const isCurrent = step.id === currentId
        const isLast = i === steps.length - 1
        return (
          <li key={step.id} className="relative flex gap-4 pb-8 last:pb-0">
            {!isLast && (
              <span
                className={`absolute left-[15px] top-8 h-[calc(100%-1.5rem)] w-px ${
                  isDone ? 'bg-brand-500' : 'bg-border'
                }`}
              />
            )}
            <span
              className={`relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border text-sm ${
                isDone
                  ? 'border-brand-500 bg-brand-500 text-white'
                  : isCurrent
                  ? 'border-brand-500 bg-white text-brand-500'
                  : 'border-border bg-white text-muted'
              }`}
            >
              {isDone ? (
                <Check size={16} strokeWidth={2.5} />
              ) : isCurrent ? (
                <span className="h-2 w-2 rounded-full bg-brand-500 animate-pulseDot" />
              ) : (
                <span className="h-1.5 w-1.5 rounded-full bg-border" />
              )}
            </span>
            <div className="pt-1">
              <p className={`text-sm font-medium ${isDone || isCurrent ? 'text-ink' : 'text-muted'}`}>
                {step.label}
              </p>
              {isCurrent && <p className="text-xs text-brand-500 mt-0.5">Processing…</p>}
              {isDone && <p className="text-xs text-success mt-0.5">Complete</p>}
            </div>
          </li>
        )
      })}
    </ol>
  )
}
