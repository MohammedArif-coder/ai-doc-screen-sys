const TONES = {
  online: 'bg-success-light text-success',
  verified: 'bg-success-light text-success',
  match: 'bg-success-light text-success',
  valid: 'bg-success-light text-success',
  pass: 'bg-success-light text-success',

  degraded: 'bg-warning-light text-warning',
  review: 'bg-warning-light text-warning',
  needs_review: 'bg-warning-light text-warning',
  warn: 'bg-warning-light text-warning',

  unavailable: 'bg-danger-light text-danger',
  failed: 'bg-danger-light text-danger',
  fail: 'bg-danger-light text-danger',
  high: 'bg-danger-light text-danger',

  not_connected: 'bg-ink/5 text-muted',
  info: 'bg-info-light text-info'
}

const LABELS = {
  online: 'Online',
  degraded: 'Degraded',
  unavailable: 'Unavailable',
  not_connected: 'Not Connected',
  verified: 'Verified',
  review: 'Review Required',
  needs_review: 'Needs Review',
  failed: 'Failed',
  match: 'Match',
  valid: 'Valid',
  pass: 'Pass',
  warn: 'Attention',
  high: 'High Risk'
}

export default function StatusPill({ tone = 'info', label, dot = false, size = 'md' }) {
  const cls = TONES[tone] || TONES.info
  const text = label || LABELS[tone] || tone
  const sizeCls = size === 'sm' ? 'text-[11px] px-2 py-0.5' : 'text-xs px-2.5 py-1'
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full font-medium ${sizeCls} ${cls}`}>
      {dot && <span className="h-1.5 w-1.5 rounded-full bg-current" />}
      {text}
    </span>
  )
}
