import { useState, useEffect } from 'react'
import { Navbar } from './components/Navbar'
import { UploadZone } from './components/UploadZone'
import { DemoCases } from './components/DemoCases'
import { ProcessingPipeline, PIPELINE_STAGES } from './components/ProcessingPipeline'
import { ResultHeader } from './components/ResultHeader'
import { WhyThisResult } from './components/WhyThisResult'
import { ContradictionCards } from './components/ContradictionCards'
import { EvidenceExplorer } from './components/EvidenceExplorer'
import { DocumentOverview } from './components/DocumentOverview'
import { LimitationsBox } from './components/LimitationsBox'
import { HistoryDrawer } from './components/HistoryDrawer'
import { SystemStatus } from './components/SystemStatus'

const API_URL = import.meta.env.VITE_DAKSH_API_URL || 'http://127.0.0.1:8000'

export default function App() {
  const [activeTab, setActiveTab] = useState('analysis')
  const [files, setFiles] = useState({ passport: null, visa: null, aadhaar: null, driving_licence: null, pan: null })
  const [result, setResult] = useState(null)
  const [busy, setBusy] = useState(false)
  const [currentStage, setCurrentStage] = useState(0)
  const [stageStates, setStageStates] = useState({})
  const [error, setError] = useState(null)
  const [apiHealth, setApiHealth] = useState(true)
  const [history, setHistory] = useState([])
  const [highlightedEvidenceId, setHighlightedEvidenceId] = useState(null)
  const [isDemo, setIsDemo] = useState(false)

  // Check API Health on load
  useEffect(() => {
    let active = true
    const checkHealth = async () => {
      try {
        const res = await fetch(`${API_URL}/api/health`)
        if (res.ok && active) {
          setApiHealth(true)
        }
      } catch {
        if (active) setApiHealth(false)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 12000)
    return () => {
      active = false
      clearInterval(interval)
    }
  }, [])

  // Handle Real File Analysis Submission
  const handleAnalyze = async () => {
    if (!files.passport && !files.visa && !files.aadhaar && !files.driving_licence && !files.pan) return
    if (busy) return

    setBusy(true)
    setError(null)
    setIsDemo(false)
    setCurrentStage(0)

    // Stage progression initialization
    const initialStates = {}
    PIPELINE_STAGES.forEach(s => { initialStates[s.id] = 'pending' })
    initialStates[PIPELINE_STAGES[0].id] = 'processing'
    setStageStates(initialStates)

    const formData = new FormData()
    if (files.passport?.file) formData.append('passport', files.passport.file)
    if (files.visa?.file) formData.append('visa', files.visa.file)
    if (files.aadhaar?.file) formData.append('aadhaar', files.aadhaar.file)
    if (files.driving_licence?.file) formData.append('driving_licence', files.driving_licence.file)
    if (files.pan?.file) formData.append('pan', files.pan.file)

    // Stage ticker simulation for smooth UX while waiting for API
    let stageIndex = 0
    const stageTimer = setInterval(() => {
      stageIndex++
      if (stageIndex < PIPELINE_STAGES.length - 1) {
        setCurrentStage(stageIndex)
        setStageStates(prev => ({
          ...prev,
          [PIPELINE_STAGES[stageIndex - 1].id]: 'complete',
          [PIPELINE_STAGES[stageIndex].id]: 'processing'
        }))
      }
    }, 400)

    try {
      const response = await fetch(`${API_URL}/api/screen-case`, {
        method: 'POST',
        body: formData
      })

      clearInterval(stageTimer)

      let payload = null
      try {
        payload = await response.json()
      } catch {
        throw new Error('Received malformed response from DAKSH server.')
      }

      if (!response.ok) {
        let errorMessage = payload.error || `DAKSH server returned HTTP ${response.status}.`
        if (errorMessage.includes('Traceback') || errorMessage.includes('File "')) {
          errorMessage = 'DAKSH case processing failed.'
        }

        // Handle 422 with partial case data
        if (payload.status || (payload.documents && payload.documents.length > 0)) {
          setCurrentStage(PIPELINE_STAGES.length)
          const resultPayload = {
            ...payload,
            status: payload.status || 'INCONCLUSIVE',
            headline: payload.headline || errorMessage,
            timestamp: new Date().toISOString()
          }
          setResult(resultPayload)
          setError(errorMessage)
          setHistory(prev => [resultPayload, ...prev])
          return
        }

        throw new Error(errorMessage)
      }

      // Complete all stages on HTTP 200
      setCurrentStage(PIPELINE_STAGES.length)
      const completeStates = {}
      PIPELINE_STAGES.forEach(s => { completeStates[s.id] = 'complete' })
      setStageStates(completeStates)

      // Set result and append to history
      const resultPayload = {
        ...payload,
        timestamp: new Date().toISOString()
      }
      setResult(resultPayload)
      setHistory(prev => [resultPayload, ...prev])

    } catch (err) {
      clearInterval(stageTimer)
      let cleanMsg = err.message || 'Could not connect to the DAKSH API service.'
      if (cleanMsg.includes('Traceback') || cleanMsg.includes('File "')) {
        cleanMsg = 'An internal document screening processing error occurred.'
      }
      setError(cleanMsg)

      const failedStates = { ...stageStates }
      if (PIPELINE_STAGES[stageIndex]) {
        failedStates[PIPELINE_STAGES[stageIndex].id] = 'failed'
      }
      setStageStates(failedStates)
    } finally {
      setBusy(false)
    }
  }

  // Handle Demo Case Selection
  const handleSelectDemo = (demo) => {
    setBusy(true)
    setError(null)
    setIsDemo(true)
    setCurrentStage(0)

    const initialStates = {}
    PIPELINE_STAGES.forEach(s => { initialStates[s.id] = 'pending' })
    initialStates[PIPELINE_STAGES[0].id] = 'processing'
    setStageStates(initialStates)

    let stageIndex = 0
    const stageTimer = setInterval(() => {
      stageIndex++
      if (stageIndex < PIPELINE_STAGES.length) {
        setCurrentStage(stageIndex)
        setStageStates(prev => ({
          ...prev,
          [PIPELINE_STAGES[stageIndex - 1].id]: 'complete',
          [PIPELINE_STAGES[stageIndex].id]: 'processing'
        }))
      } else {
        clearInterval(stageTimer)
        const completeStates = {}
        PIPELINE_STAGES.forEach(s => { completeStates[s.id] = 'complete' })
        setStageStates(completeStates)

        const resultPayload = {
          ...demo.data,
          timestamp: new Date().toISOString()
        }
        setResult(resultPayload)
        setHistory(prev => [resultPayload, ...prev])
        setBusy(false)
      }
    }, 200)
  }

  // Handle Reset to New Case
  const handleResetCase = () => {
    setResult(null)
    setError(null)
    setBusy(false)
    setIsDemo(false)
    setCurrentStage(0)
    setStageStates({})
    setFiles({ passport: null, visa: null, aadhaar: null, driving_licence: null, pan: null })
  }

  // Handle Clicking Evidence ID Chip in Contradiction Card
  const handleJumpToEvidence = (evidenceId) => {
    setHighlightedEvidenceId(evidenceId)
    setActiveTab('evidence')
  }

  return (
    <div className="app-layout">
      {/* Top Header / Navigation Bar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        apiHealth={apiHealth}
        onResetCase={handleResetCase}
      />

      {/* Main Content View Area */}
      <main className="main-content">
        {/* TAB 1: CASE ANALYSIS */}
        {activeTab === 'analysis' && (
          <div className="analysis-view-space">
            {/* If no result present, show upload area and demo cases */}
            {!result ? (
              <>
                <UploadZone
                  files={files}
                  setFiles={setFiles}
                  onAnalyze={handleAnalyze}
                  busy={busy}
                />

                {busy && (
                  <ProcessingPipeline
                    currentStage={currentStage}
                    completed={false}
                    stageStates={stageStates}
                  />
                )}

                {error && (
                  <div className="error-alert panel">
                    <div className="error-icon">✕</div>
                    <div className="error-content">
                      <h4>Processing Error</h4>
                      <p>{error}</p>
                    </div>
                    <button type="button" className="btn-dismiss" onClick={() => setError(null)}>
                      Dismiss
                    </button>
                  </div>
                )}

                <DemoCases
                  onSelectDemo={handleSelectDemo}
                  busy={busy}
                />
              </>
            ) : (
              /* SCREENING RESULT DASHBOARD */
              <div className="result-dashboard-space">
                {/* Result Header & 5-Second Executive Summary */}
                <ResultHeader
                  result={result}
                  onReset={handleResetCase}
                  isDemo={isDemo}
                />

                {/* Processing Pipeline Tracker (Completed) */}
                <ProcessingPipeline
                  currentStage={PIPELINE_STAGES.length}
                  completed={true}
                  stageStates={stageStates}
                />

                {/* Why This Result? & Reviewer Guidance */}
                <WhyThisResult
                  reasons={result.reasons}
                  nextActions={result.next_actions}
                  contradictions={result.contradictions}
                />

                {/* Cross-Document Contradiction Cards */}
                <ContradictionCards
                  contradictions={result.contradictions}
                  evidence={result.evidence}
                  onSelectEvidenceId={handleJumpToEvidence}
                />

                {/* System Limitations & Adapter Errors (if any) */}
                <LimitationsBox
                  adapterErrors={result.adapter_errors}
                  reasons={result.reasons}
                />

                {/* Document Intake Overview */}
                <DocumentOverview
                  documents={result.documents}
                  evidence={result.evidence}
                  adapterErrors={result.adapter_errors}
                  files={files}
                />

                {/* Evidence Register Section */}
                <EvidenceExplorer
                  evidence={result.evidence}
                  highlightedId={highlightedEvidenceId}
                />
              </div>
            )}
          </div>
        )}

        {/* TAB 2: EVIDENCE EXPLORER */}
        {activeTab === 'evidence' && (
          <div className="evidence-tab-space">
            {result ? (
              <EvidenceExplorer
                evidence={result.evidence}
                highlightedId={highlightedEvidenceId}
              />
            ) : (
              <section className="panel empty-tab-panel">
                <h3>No Case Results Loaded</h3>
                <p>Please upload documents or select a demo case in <strong>Case Analysis</strong> tab first to explore evidence items.</p>
                <button type="button" className="btn-primary" onClick={() => setActiveTab('analysis')}>
                  Go to Case Analysis
                </button>
              </section>
            )}
          </div>
        )}

        {/* TAB 3: HISTORY */}
        {activeTab === 'history' && (
          <HistoryDrawer
            history={history}
            onSelectCase={(selectedItem) => {
              setResult(selectedItem)
              setActiveTab('analysis')
            }}
            onClearHistory={() => setHistory([])}
          />
        )}

        {/* TAB 4: SYSTEM STATUS */}
        {activeTab === 'status' && (
          <SystemStatus apiHealth={apiHealth} />
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <span>DAKSH P6 · Document Authentication & Knowledge-based Screening Hub</span>
          <span className="footer-sub">Deterministic Review Priority & Cross-Document Traceability Engine</span>
        </div>
      </footer>
    </div>
  )
}
