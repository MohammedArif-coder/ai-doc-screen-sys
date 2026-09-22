import { useMemo, useState } from 'react'

const API_URL = import.meta.env.VITE_DAKSH_API_URL || 'http://127.0.0.1:8000'

const PIPELINE = [
  ['01', 'Documents received', 'Secure temporary intake'],
  ['02', 'Document analysis', 'Module-specific checks'],
  ['03', 'Evidence extraction', 'Normalized findings'],
  ['04', 'Consistency', 'Cross-document comparison'],
  ['05', 'Review priority', 'Deterministic aggregation'],
  ['06', 'Decision', 'Explainable result'],
]

const DOCUMENTS = [
  { key: 'passport', label: 'Passport', required: false, hint: 'Optional identity document' },
  { key: 'visa', label: 'Visa', required: false, hint: 'Optional travel document' },
  { key: 'aadhaar', label: 'Aadhaar', required: false, hint: 'Optional identity evidence' },
]

function StatusBadge({ value }) {
  return <span className={`badge badge-${String(value || 'unknown').toLowerCase()}`}>{value || 'UNKNOWN'}</span>
}

function FilePicker({ definition, file, onChange, onRemove }) {
  return (
    <label className={`dropzone ${file ? 'has-file' : ''}`}>
      <input
        type="file"
        accept=".jpg,.jpeg,.png,.pdf,image/jpeg,image/png,application/pdf"
        onChange={(event) => onChange(event.target.files?.[0] || null)}
      />
      <span className="drop-icon">{file ? '✓' : '+'}</span>
      <span className="drop-title">{definition.label}{definition.required && <em>Required</em>}</span>
      <span className="drop-hint">{file ? file.name : definition.hint}</span>
      <span className="drop-meta">{file ? 'Click to replace' : 'JPG, PNG, or PDF'}</span>
      {file && <button type="button" className="remove-file" onClick={(event) => { event.preventDefault(); onRemove() }}>Remove</button>}
    </label>
  )
}

function Pipeline({ active, complete }) {
  return (
    <section className="pipeline panel">
      <div className="section-title">
        <div><p className="kicker">DAKSH reasoning chain</p><h2>Evidence to decision</h2></div>
        <span className="pipeline-note">{complete ? 'Complete' : 'Ready for screening'}</span>
      </div>
      <div className="pipeline-track">
        {PIPELINE.map(([number, title, detail], index) => (
          <div className={`pipeline-step ${index < active ? 'complete' : ''} ${index === active && !complete ? 'active' : ''}`} key={number}>
            <span className="step-number">{index < active || complete ? '✓' : number}</span>
            <strong>{title}</strong>
            <small>{detail}</small>
          </div>
        ))}
      </div>
    </section>
  )
}

function DocumentSummary({ documents, evidence }) {
  return (
    <section className="panel">
      <div className="section-title"><div><p className="kicker">Case inputs</p><h2>Documents processed</h2></div><span className="muted">{documents?.length || 0} documents</span></div>
      <div className="document-grid">
        {documents?.map((document) => {
          const count = evidence?.filter((item) => item.document_id === document.document_id).length || 0
          return (
            <article className="document-card" key={document.document_id}>
              <div className="document-card-top"><span className="document-mark">{document.document_type.slice(0, 1)}</span><StatusBadge value={document.processing_status} /></div>
              <h3>{document.document_type}</h3>
              <p>{document.document_id}</p>
              <footer><span>{count} evidence items</span><span>{document.source_module}</span></footer>
            </article>
          )
        })}
      </div>
    </section>
  )
}

function ContradictionCard({ item }) {
  return (
    <article className="contradiction-card">
      <div className="contradiction-heading"><div><p className="kicker">Cross-document inconsistency</p><h3>{item.field.replaceAll('_', ' ')}</h3></div><StatusBadge value={item.severity} /></div>
      <div className="value-compare"><div><small>{item.document_a}</small><strong>{String(item.value_a)}</strong></div><span className="not-equal">≠</span><div><small>{item.document_b}</small><strong>{String(item.value_b)}</strong></div></div>
      <p className="explanation">{item.explanation}</p>
      <div className="trace-row"><span>Evidence IDs</span><strong>{item.evidence_ids?.length ? item.evidence_ids.join(' · ') : 'See source evidence'}</strong></div>
    </article>
  )
}

function EvidenceTable({ evidence }) {
  const [filter, setFilter] = useState('all')
  const sources = useMemo(() => ['all', ...new Set((evidence || []).map((item) => item.source.split('.')[0]))], [evidence])
  const visible = filter === 'all' ? evidence : evidence?.filter((item) => item.source.startsWith(`${filter}.`))
  return (
    <section className="panel evidence-panel">
      <div className="section-title"><div><p className="kicker">Traceability</p><h2>Evidence register</h2></div><select value={filter} onChange={(event) => setFilter(event.target.value)}>{sources.map((source) => <option value={source} key={source}>{source === 'all' ? 'All sources' : source}</option>)}</select></div>
      <div className="table-scroll"><table><thead><tr><th>Source</th><th>Field</th><th>Finding</th><th>Confidence</th><th>Severity</th></tr></thead><tbody>{visible?.map((item) => <tr key={item.evidence_id}><td><span className="source-chip">{item.source}</span></td><td>{item.field}</td><td className="finding">{typeof item.value === 'object' ? JSON.stringify(item.value) : String(item.value)}</td><td>{item.confidence == null ? 'Unavailable' : item.confidence}</td><td>{item.severity || '—'}</td></tr>)}</tbody></table></div>
    </section>
  )
}

function ResultDashboard({ result, onReset }) {
  return (
    <main className="dashboard">
      <div className="topbar"><div className="wordmark">DAKSH <span>P6</span></div><div className="topbar-actions"><span className="live-dot">API connected</span><button className="outline-button" onClick={onReset}>New case</button></div></div>
      <div className="case-banner"><div><p className="kicker">Screening case</p><h1>{result.case_id}</h1><p className="muted">Generated from the available document evidence</p></div><div className="decision"><StatusBadge value={result.status} /><strong>{result.review_required ? 'Review required' : 'No review required'}</strong></div></div>
      <Pipeline active={PIPELINE.length} complete />
      <section className="headline panel"><p className="kicker">Decision headline</p><h2>{result.headline}</h2><p>{result.review_required ? 'The evidence chain contains signals that should be checked by a human reviewer.' : 'No significant inconsistency was detected in the available evidence.'}</p></section>
      <DocumentSummary documents={result.documents} evidence={result.evidence} />
      {result.adapter_errors?.length > 0 && <section className="panel limitation"><p className="kicker">Processing limitation</p><h2>Some checks were unavailable</h2><ul>{result.adapter_errors.map((error) => <li key={error}>{error}</li>)}</ul></section>}
      <section className="reason-grid"><section className="panel"><p className="kicker">Explainability</p><h2>Why this result?</h2>{result.reasons?.length ? <ol className="reason-list">{result.reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>)}</ol> : <p className="muted">No concerning signals were produced.</p>}</section><section className="panel action-panel"><p className="kicker">Reviewer guidance</p><h2>Recommended next actions</h2><ul>{result.next_actions?.map((action) => <li key={action}>{action}</li>)}</ul></section></section>
      <section className="panel"><div className="section-title"><div><p className="kicker">Traceable findings</p><h2>Contradictions</h2></div><span className="muted">{result.contradictions?.length || 0} found</span></div>{result.contradictions?.length ? <div className="contradiction-list">{result.contradictions.map((item) => <ContradictionCard item={item} key={item.contradiction_id} />)}</div> : <div className="empty-state">No cross-document inconsistency detected.</div>}</section>
      <EvidenceTable evidence={result.evidence} />
      <footer className="dashboard-footer">DAKSH is an evidence-based review-prioritisation system. It is not official identity authentication.</footer>
    </main>
  )
}

export default function App() {
  const [files, setFiles] = useState({ passport: null, visa: null, aadhaar: null })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [activeStage, setActiveStage] = useState(0)

  const canSubmit = Boolean((files.passport || files.visa || files.aadhaar) && !busy)

  async function submit(event) {
    event.preventDefault()
    if (!canSubmit) return
    setBusy(true)
    setError('')
    setActiveStage(1)
    const form = new FormData()
    if (files.passport) form.append('passport', files.passport)
    if (files.visa) form.append('visa', files.visa)
    if (files.aadhaar) form.append('aadhaar', files.aadhaar)
    try {
      const response = await fetch(`${API_URL}/api/screen-case`, { method: 'POST', body: form })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.error || 'DAKSH could not process this case.')
      setActiveStage(PIPELINE.length)
      setResult(payload)
    } catch (requestError) {
      setError(requestError.message || 'Could not connect to the DAKSH API.')
    } finally {
      setBusy(false)
    }
  }

  if (result) return <ResultDashboard result={result} onReset={() => { setResult(null); setFiles({ passport: null, visa: null, aadhaar: null }) }} />

  return (
    <main className="app-shell">
      <div className="topbar"><div className="wordmark">DAKSH <span>P6</span></div><div className="topbar-actions"><span className="live-dot">Review workspace</span><a href={`${API_URL}/docs`} target="_blank" rel="noreferrer">API docs ↗</a></div></div>
      <section className="hero"><div><p className="kicker">Document Authentication & Knowledge-based Screening Hub</p><h1>One evidence chain.<br /><span>Clearer review decisions.</span></h1><p>Bring Passport, Visa, and Aadhaar evidence together. DAKSH identifies supported cross-document inconsistencies and explains what a reviewer should verify next.</p></div><div className="hero-seal"><strong>P6</strong><span>Evidence-led<br />screening</span></div></section>
      <Pipeline active={activeStage} />
      <form className="panel intake" onSubmit={submit}>
        <div className="section-title"><div><p className="kicker">Case intake</p><h2>Upload documents</h2></div><span className="muted">Files are processed temporarily</span></div>
        <div className="picker-grid">{DOCUMENTS.map((definition) => <FilePicker key={definition.key} definition={definition} file={files[definition.key]} onChange={(file) => setFiles({ ...files, [definition.key]: file })} onRemove={() => setFiles({ ...files, [definition.key]: null })} />)}</div>
        {busy && <div className="processing-bar"><span className="spinner" /> Screening through the DAKSH reasoning chain…</div>}
        {error && <div className="error-box"><strong>Processing could not be completed</strong><span>{error}</span><button type="button" onClick={() => setError('')}>Dismiss</button></div>}
        <div className="intake-footer"><p><span className="lock">●</span> Upload any one or more documents. Files are not stored by this prototype.</p><button className="primary-button" disabled={!canSubmit}>{busy ? 'Screening…' : 'Start screening'}</button></div>
      </form>
      <section className="principles"><div><strong>Evidence first</strong><span>Every signal remains traceable to a source document.</span></div><div><strong>No automatic fake label</strong><span>Contradictions create review priority, not a final authenticity verdict.</span></div><div><strong>Human in the loop</strong><span>The final verification decision remains with the reviewer.</span></div></section>
      <footer className="dashboard-footer">DAKSH P6 · Local prototype · API {API_URL}</footer>
    </main>
  )
}
