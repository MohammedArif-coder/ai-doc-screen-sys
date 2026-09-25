import { useEffect, useState, useRef } from 'react'
import { useLocation, useNavigate, Navigate } from 'react-router-dom'
import { MULTI_DOC_ENGINE } from '../config/modules.js'
import { verifyCase } from '../api/multiDocumentApi.js'
import PipelineSteps from '../components/PipelineSteps.jsx'

export default function MultiProcessing() {
  const { state } = useLocation()
  const navigate = useNavigate()
  const docs = state?.docs || []
  const [current, setCurrent] = useState(MULTI_DOC_ENGINE.stages[0])
  const [done, setDone] = useState([])
  const [error, setError] = useState(null)
  const started = useRef(false)

  useEffect(() => {
    if (!docs.length || started.current) return
    started.current = true

    async function run() {
      try {
        const result = await verifyCase(docs, {
          onStage: (stage) => {
            const idx = MULTI_DOC_ENGINE.stages.indexOf(stage)
            setDone(MULTI_DOC_ENGINE.stages.slice(0, idx))
            setCurrent(stage)
          }
        })
        setDone(MULTI_DOC_ENGINE.stages)
        setCurrent(null)
        setTimeout(() => navigate('/multi/result', { state: { result } }), 500)
      } catch (err) {
        setError(err)
      }
    }
    run()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [docs])

  if (!docs.length) return <Navigate to="/multi" replace />

  const steps = MULTI_DOC_ENGINE.stages.map((s) => ({ id: s, label: s }))

  return (
    <div className="mx-auto max-w-xl px-6 py-14">
      <p className="text-sm font-medium text-engine">Multi-Document Verification</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">
        Running the DAKSH Intelligence Engine
      </h1>
      <p className="mt-2 text-sm text-muted">
        Correlating {docs.length} documents belonging to this case.
      </p>

      {error ? (
        <div className="mt-8 rounded-md border border-danger-light bg-danger-light px-5 py-4">
          <p className="text-sm font-medium text-danger">Analysis failed</p>
          <p className="mt-1 text-sm text-danger/80">{error.message}</p>
        </div>
      ) : (
        <div className="mt-10 rounded-lg border border-engine/25 bg-white p-7 shadow-card">
          <PipelineSteps steps={steps} currentId={current} doneIds={done} />
        </div>
      )}
    </div>
  )
}
