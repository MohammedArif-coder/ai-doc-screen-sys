import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getModule } from '../config/modules.js'
import { verifyDocument } from '../api/moduleApi.js'
import PipelineSteps from '../components/PipelineSteps.jsx'

const STAGE_LABELS = {
  upload: 'Document Received',
  ocr: 'OCR Extraction',
  validation: 'Field Validation',
  forensics: 'Forensic Analysis',
  result: 'Final Result'
}
const STEP_ORDER = ['upload', 'ocr', 'validation', 'forensics', 'result']

export default function IndividualProcessing() {
  const { moduleId } = useParams()
  const navigate = useNavigate()
  const mod = getModule(moduleId)
  const [current, setCurrent] = useState('upload')
  const [done, setDone] = useState([])
  const [error, setError] = useState(null)
  const started = useRef(false)

  useEffect(() => {
    if (started.current) return
    started.current = true

    async function run() {
      try {
        const result = await verifyDocument(moduleId, null, {
          onStage: (stage) => {
            setDone((prev) => {
              const idx = STEP_ORDER.indexOf(stage)
              return STEP_ORDER.slice(0, idx)
            })
            setCurrent(stage)
          }
        })
        setDone(STEP_ORDER)
        setCurrent(null)
        setTimeout(() => navigate(`/individual/${moduleId}/result`, { state: { result } }), 500)
      } catch (err) {
        setError(err)
      }
    }
    run()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [moduleId])

  if (!mod) return <div className="p-10 text-sm text-muted">Unknown module.</div>

  const steps = STEP_ORDER.map((id) => ({ id, label: STAGE_LABELS[id] }))

  return (
    <div className="mx-auto max-w-xl px-6 py-14">
      <p className="text-sm font-medium text-brand-500">Individual Verification · {mod.name}</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">Screening in progress</h1>
      <p className="mt-2 text-sm text-muted">
        Running the {mod.name} module pipeline. This usually takes a few seconds.
      </p>

      {error ? (
        <div className="mt-8 rounded-md border border-danger-light bg-danger-light px-5 py-4">
          <p className="text-sm font-medium text-danger">Screening failed</p>
          <p className="mt-1 text-sm text-danger/80">{error.message}</p>
          <p className="mt-2 text-xs text-danger/70">
            Stage: {error.stage || 'unknown'} · {error.retryable ? 'You can retry this step.' : 'Retry is not available for this error.'}
          </p>
          {error.retryable && (
            <button
              onClick={() => window.location.reload()}
              className="mt-3 rounded-md bg-danger px-4 py-2 text-xs font-medium text-white hover:opacity-90"
            >
              Retry
            </button>
          )}
        </div>
      ) : (
        <div className="mt-10 rounded-lg border border-border bg-white p-7 shadow-card">
          <PipelineSteps steps={steps} currentId={current} doneIds={done} />
        </div>
      )}
    </div>
  )
}
