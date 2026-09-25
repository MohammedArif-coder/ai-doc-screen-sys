import React, { useState, useEffect } from 'react';
import { ShieldCheck, ScanLine, AlertCircle, Activity, Target, Download, CheckCircle2, AlertTriangle, FileText } from 'lucide-react';
import UploadZone from '../components/UploadZone';
import DemoVisaSelector from '../components/DemoVisaSelector';
import DocumentPreview from '../components/DocumentPreview';
import ScoreCard from '../components/ScoreCard';
import OCRPanel from '../components/OCRPanel';
import StatusBadge from '../components/StatusBadge';
import { api } from '../services/api';

export default function VisaScreening({ demos = [], result, setResult }) {
  const [selectedDemoId, setSelectedDemoId] = useState('DEMO-01');
  const [activeUploadId, setActiveUploadId] = useState(null);
  const [previewSrc, setPreviewSrc] = useState('');
  const [loading, setLoading] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');

  // Auto-run DEMO-01 on first load if no result exists
  useEffect(() => {
    if (!result && selectedDemoId) {
      handleRunDemo('DEMO-01');
    } else if (!activeUploadId && selectedDemoId) {
      setPreviewSrc(api.imageUrl(`/api/demo/documents/${selectedDemoId}/image`));
    }
  }, [selectedDemoId]);

  const handleRunDemo = async (demoId) => {
    const idToRun = demoId || selectedDemoId;
    setSelectedDemoId(idToRun);
    setActiveUploadId(null);
    setPreviewSrc(api.imageUrl(`/api/demo/documents/${idToRun}/image`));
    setLoading(true);
    setError('');

    try {
      const res = await api.analyzeDemo(idToRun);
      setResult(res);
    } catch (err) {
      setError(err.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError('');
    try {
      const uploadRes = await api.upload(file);
      setActiveUploadId(uploadRes.upload_id);
      const fullUrl = api.imageUrl(uploadRes.preview_url);
      setPreviewSrc(fullUrl);

      const analysisRes = await api.analyzeUpload(uploadRes.upload_id);
      setResult(analysisRes);
    } catch (err) {
      setError(err.message || 'Document upload analysis failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadReport = async () => {
    if (!result) return;
    setDownloading(true);
    try {
      const blob = await api.generateReport(result);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `daksh-screening-report-${result.document_id || 'VISA'}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Report download error: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const authScore = result?.authenticity_score ?? (result?.scores?.ocr ?? 95);
  const isOriginal = result?.verdict === 'ORIGINAL / AUTHENTIC' || authScore >= 90;
  const isTampered = result?.verdict === 'TAMPERED DOCUMENT' || (result?.tamper_analysis?.signal_detected);
  const regions = result?.tamper_analysis?.regions || [];

  return (
    <div className="screening-page" style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Direct Clean Header */}
      <div className="section-title" style={{ marginBottom: '20px' }}>
        <div>
          <div className="eyebrow" style={{ color: 'var(--blue)' }}>
            VISA AUTHENTICITY & TAMPER DETECTOR
          </div>
          <h1 style={{ fontSize: '26px', margin: '6px 0 4px' }}>Visa Document Check</h1>
          <p style={{ fontSize: '13px' }}>
            Upload a visa or select a demo case to verify if it is Original (90-100% score) or Tampered, and get the exact anomaly location.
          </p>
        </div>
      </div>

      {/* Control Row: Uploader + Demo Selector */}
      <div className="screening-layout" style={{ gridTemplateColumns: '360px 1fr', gap: '20px' }}>
        <div>
          <UploadZone
            onFileSelected={handleFileUpload}
            onSelectDemo={() => handleRunDemo(selectedDemoId)}
            loading={loading}
          />

          <div className="panel" style={{ marginTop: '16px', padding: '16px' }}>
            <DemoVisaSelector
              demos={demos}
              selectedId={selectedDemoId}
              onSelect={(id) => {
                setSelectedDemoId(id);
                handleRunDemo(id);
              }}
              loading={loading}
            />

            <button
              className="primary-btn full"
              style={{ marginTop: '14px', padding: '12px', fontSize: '13px' }}
              onClick={() => handleRunDemo(selectedDemoId)}
              disabled={loading}
            >
              {loading ? <Activity className="spin" size={18} /> : <ScanLine size={18} />}
              {loading ? 'Checking Authenticity...' : 'CHECK VISA AUTHENTICITY'}
            </button>

            {error && (
              <div className="error-box" style={{ marginTop: '10px', fontSize: '11px', color: 'var(--red)' }}>
                <AlertCircle size={14} style={{ display: 'inline', marginRight: '4px' }} />
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Visual Document Viewer Canvas */}
        <div>
          <DocumentPreview
            imageSrc={previewSrc}
            documentId={activeUploadId ? 'UPLOADED-VISA' : selectedDemoId}
            result={result}
          />
        </div>
      </div>

      {/* Main Results Display */}
      {result && (
        <div className="results" style={{ marginTop: '24px' }}>
          {/* Main Verdict Banner */}
          <div
            className="result-banner"
            style={{
              background: isOriginal ? 'linear-gradient(135deg, #0a3321 0%, #061f14 100%)' : isTampered ? 'linear-gradient(135deg, #421414 0%, #290808 100%)' : 'linear-gradient(135deg, #38290e 0%, #211707 100%)',
              border: `2px solid ${isOriginal ? 'var(--green)' : isTampered ? 'var(--red)' : 'var(--amber)'}`,
              padding: '24px 28px',
              borderRadius: '8px'
            }}
          >
            <div>
              <div className="panel-kicker" style={{ color: isOriginal ? 'var(--green)' : isTampered ? '#f87171' : 'var(--amber)' }}>
                {isOriginal ? '✓ AUTHENTIC VISA DOCUMENT' : '⚠ TAMPERED / ANOMALY DETECTED'}
              </div>
              <h2 style={{ fontSize: '30px', margin: '8px 0', color: '#ffffff' }}>
                {result.verdict || (isOriginal ? 'ORIGINAL / AUTHENTIC' : isTampered ? 'TAMPERED DOCUMENT' : 'SUSPICIOUS / REVIEW REQUIRED')}
              </h2>
              <p style={{ fontSize: '13px', color: '#e2edf2' }}>{result.reason}</p>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: '#9bb0c0', letterSpacing: '0.1em' }}>AUTHENTICITY SCORE</div>
              <div style={{ fontSize: '48px', fontWeight: 800, fontFamily: 'Space Grotesk', color: isOriginal ? 'var(--green)' : isTampered ? 'var(--red)' : 'var(--amber)' }}>
                {authScore}%
              </div>
              <StatusBadge status={result.status} />
            </div>
          </div>

          {/* Exact Anomaly Location Box */}
          {regions.length > 0 ? (
            <div
              className="panel"
              style={{
                marginTop: '16px',
                background: '#1c1010',
                border: '1px solid #7f1d1d',
                padding: '16px 20px'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#f87171', fontWeight: 700, fontSize: '14px' }}>
                <Target size={18} />
                EXACT ANOMALY LOCATION DETECTED:
              </div>
              <div style={{ marginTop: '10px', display: 'grid', gap: '8px' }}>
                {regions.map((reg, idx) => (
                  <div
                    key={idx}
                    style={{
                      background: '#2b1414',
                      border: '1px solid #991b1b',
                      borderRadius: '6px',
                      padding: '10px 14px',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      fontSize: '12px',
                      color: '#fca5a5'
                    }}
                  >
                    <div>
                      <strong style={{ color: '#ffffff', fontSize: '13px' }}>{reg.label}</strong>
                      <span style={{ marginLeft: '12px', fontSize: '11px', color: '#fca5a5' }}>
                        Located at X: {reg.x}% · Y: {reg.y}% (Width: {reg.width}%, Height: {reg.height}%)
                      </span>
                    </div>
                    <span className="badge danger">RED BOX HIGHLIGHTED ON VISA</span>
                  </div>
                ))}
              </div>
            </div>
          ) : isOriginal ? (
            <div
              className="panel"
              style={{
                marginTop: '16px',
                background: '#092117',
                border: '1px solid #15803d',
                padding: '14px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                color: 'var(--green)',
                fontSize: '13px',
                fontWeight: 600
              }}
            >
              <CheckCircle2 size={18} />
              100% Clean Baseline — No image tampering or field anomalies detected.
            </div>
          ) : null}

          {/* Extracted Fields Table & Report Download */}
          <div className="result-columns" style={{ marginTop: '16px' }}>
            <OCRPanel ocrData={result.ocr} />

            <div className="panel" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <div className="panel-head">
                  <h2>Authenticity Breakdown</h2>
                  <span>Score {authScore}%</span>
                </div>

                <div style={{ display: 'grid', gap: '10px', margin: '14px 0' }}>
                  <ScoreCard
                    title="Authenticity Score"
                    score={authScore}
                    tone={isOriginal ? 'green' : 'red'}
                    statusLabel={isOriginal ? 'ORIGINAL (CLEAN)' : 'TAMPERED / FAKE'}
                  />
                  <ScoreCard
                    title="OCR Readability"
                    score={result.scores?.ocr ?? 94}
                    statusLabel="TEXT EXTRACTED"
                  />
                  <ScoreCard
                    title="Image Quality"
                    score={result.scores?.image_quality ?? 88}
                    statusLabel={result.scores?.image_quality >= 70 ? 'CLEAR RESOLUTION' : 'BLURRED IMAGE'}
                  />
                </div>
              </div>

              <button
                className="primary-btn full"
                onClick={handleDownloadReport}
                disabled={downloading}
                style={{ padding: '12px', justifyContent: 'center' }}
              >
                <Download size={17} />
                {downloading ? 'Generating Report...' : 'Download PDF Screening Report'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
