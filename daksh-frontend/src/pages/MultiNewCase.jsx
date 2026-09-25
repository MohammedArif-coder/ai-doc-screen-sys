import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, X, Network, ArrowRight } from 'lucide-react'
import { MODULES } from '../config/modules.js'

export default function MultiNewCase() {
  const navigate = useNavigate()
  const [docs, setDocs] = useState([])
  const [picking, setPicking] = useState(false)

  function addDoc(moduleId) {
    const mod = MODULES.find((m) => m.id === moduleId)
    setDocs((d) => [...d, { key: `${moduleId}-${Date.now()}`, moduleId, name: mod.name }])
    setPicking(false)
  }

  function removeDoc(key) {
    setDocs((d) => d.filter((doc) => doc.key !== key))
  }

  return (
    <div className="mx-auto max-w-3xl px-6 py-10">
      <div className="flex items-center gap-2.5">
        <div className="flex h-9 w-9 items-center justify-center rounded-md bg-engine text-white">
          <Network size={17} />
        </div>
        <div>
          <p className="text-sm font-medium text-engine">Multi-Document Verification</p>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">New case</h1>
        </div>
      </div>
      <p className="mt-3 max-w-lg text-sm text-muted">
        Add every document that belongs to the same identity. DAKSH screens each one individually,
        then correlates the results.
      </p>

      <div className="mt-8 rounded-lg border border-border bg-white p-6 shadow-card">
        {docs.length === 0 ? (
          <div className="rounded-md border border-dashed border-border py-10 text-center">
            <p className="text-sm text-muted">No documents added yet.</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {docs.map((d) => (
              <li
                key={d.key}
                className="flex items-center justify-between rounded-md border border-border bg-bg px-4 py-3"
              >
                <span className="text-sm font-medium text-ink">{d.name}</span>
                <button onClick={() => removeDoc(d.key)} className="text-muted hover:text-danger" aria-label={`Remove ${d.name}`}>
                  <X size={15} />
                </button>
              </li>
            ))}
          </ul>
        )}

        <div className="relative mt-4">
          <button
            onClick={() => setPicking((p) => !p)}
            className="flex w-full items-center justify-center gap-2 rounded-md border border-dashed border-brand-300 py-3 text-sm font-medium text-brand-700 hover:bg-brand-50"
          >
            <Plus size={16} /> Upload Document
          </button>
          {picking && (
            <div className="absolute left-0 right-0 top-full z-10 mt-2 rounded-md border border-border bg-white p-2 shadow-raised">
              {MODULES.map((m) => (
                <button
                  key={m.id}
                  onClick={() => addDoc(m.id)}
                  className="flex w-full items-center justify-between rounded-md px-3 py-2 text-left text-sm hover:bg-ink/[0.03]"
                >
                  <span className="text-ink">{m.name}</span>
                  <span className="text-[11px] text-muted">{m.shortName}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <button
        disabled={docs.length < 2}
        onClick={() => navigate('/multi/processing', { state: { docs } })}
        className="mt-6 flex w-full items-center justify-center gap-2 rounded-md bg-engine py-3 text-sm font-medium text-white transition-colors hover:bg-engine-dark disabled:cursor-not-allowed disabled:bg-border disabled:text-muted"
      >
        Run Cross-Document Analysis
        <ArrowRight size={15} />
      </button>
      {docs.length < 2 && (
        <p className="mt-2 text-center text-xs text-muted">Add at least two documents to correlate.</p>
      )}
    </div>
  )
}
