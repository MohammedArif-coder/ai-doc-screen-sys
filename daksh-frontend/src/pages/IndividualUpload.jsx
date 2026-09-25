import { useState, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { UploadCloud, FileText, X, ChevronLeft } from 'lucide-react'
import { getModule } from '../config/modules.js'

export default function IndividualUpload() {
  const { moduleId } = useParams()
  const navigate = useNavigate()
  const mod = getModule(moduleId)
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  if (!mod) return <div className="p-10 text-sm text-muted">Unknown module.</div>

  function handleFiles(files) {
    if (files?.[0]) setFile(files[0])
  }

  function handleContinue() {
    // File is passed via router state; in a real build, hold it in a case
    // store. Kept simple here since processing is demo/mocked either way.
    navigate(`/individual/${moduleId}/processing`, { state: { fileName: file?.name } })
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-10">
      <Link to="/individual" className="flex items-center gap-1 text-xs font-medium text-muted hover:text-ink">
        <ChevronLeft size={14} /> Back to document selection
      </Link>

      <p className="mt-4 text-sm font-medium text-brand-500">Individual Verification · {mod.name}</p>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight text-ink">Upload the document</h1>
      <p className="mt-2 text-sm text-muted">Accepted formats: {mod.supportedFormats.join(', ')}</p>

      <div
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragOver(false)
          handleFiles(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        className={`mt-6 flex cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed px-6 py-14 text-center transition-colors ${
          dragOver ? 'border-brand-500 bg-brand-50' : 'border-border bg-white hover:bg-ink/[0.015]'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="image/*,.pdf"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        <div className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-50 text-brand-700">
          <UploadCloud size={20} strokeWidth={2} />
        </div>
        <p className="mt-4 text-sm font-medium text-ink">Drag and drop, or click to browse</p>
        <p className="mt-1 text-xs text-muted">Maximum 10 MB · one file</p>
      </div>

      {file && (
        <div className="mt-4 flex items-center justify-between rounded-md border border-border bg-white px-4 py-3">
          <div className="flex items-center gap-3">
            <FileText size={17} className="text-brand-700" />
            <span className="text-sm text-ink">{file.name}</span>
          </div>
          <button onClick={() => setFile(null)} className="text-muted hover:text-ink" aria-label="Remove file">
            <X size={16} />
          </button>
        </div>
      )}

      <button
        disabled={!file}
        onClick={handleContinue}
        className="mt-8 w-full rounded-md bg-brand-700 py-3 text-sm font-medium text-white transition-colors hover:bg-brand-900 disabled:cursor-not-allowed disabled:bg-border disabled:text-muted"
      >
        Start Screening
      </button>
    </div>
  )
}
