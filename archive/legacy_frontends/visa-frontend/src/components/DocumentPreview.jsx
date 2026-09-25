import React, { useState } from 'react';
import { ZoomIn, ZoomOut, RotateCcw, AlertTriangle } from 'lucide-react';
import StatusBadge from './StatusBadge';
import TamperHeatmap from './TamperHeatmap';

export default function DocumentPreview({
  imageSrc,
  documentId = 'DEMO-000123',
  result,
  watermark = 'DEMO – NOT A REAL VISA'
}) {
  const [zoom, setZoom] = useState(1);

  const handleZoomIn = () => setZoom((z) => Math.min(z + 0.25, 2.5));
  const handleZoomOut = () => setZoom((z) => Math.max(z - 0.25, 0.75));
  const handleReset = () => setZoom(1);

  const regions = result?.tamper_analysis?.regions || [];

  return (
    <div className="panel document-panel">
      <div className="panel-head">
        <div>
          <div className="panel-kicker">DOCUMENT CANVAS VIEWER</div>
          <h2>
            {documentId} <span className="watermark-tag">FICTIONAL</span>
          </h2>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ display: 'flex', gap: '4px', background: '#0a1a27', padding: '4px', borderRadius: '4px' }}>
            <button className="icon-btn" onClick={handleZoomOut} title="Zoom Out" aria-label="Zoom Out">
              <ZoomOut size={15} />
            </button>
            <button className="icon-btn" onClick={handleReset} title="Reset Zoom" aria-label="Reset Zoom">
              <RotateCcw size={15} />
            </button>
            <button className="icon-btn" onClick={handleZoomIn} title="Zoom In" aria-label="Zoom In">
              <ZoomIn size={15} />
            </button>
          </div>
          <StatusBadge status={result?.status || 'ready'}>
            {result ? result.status.replace('_', ' ').toUpperCase() : 'READY'}
          </StatusBadge>
        </div>
      </div>

      <div className="document-stage">
        {imageSrc ? (
          <div style={{ position: 'relative', transform: `scale(${zoom})`, transition: 'transform 0.2s ease' }}>
            <img src={imageSrc} alt="Synthetic Visa Document" />
            
            {/* Tamper bounding box overlays */}
            {regions.map((region, idx) => (
              <div
                key={idx}
                className="highlight"
                style={{
                  left: `${region.x}%`,
                  top: `${region.y}%`,
                  width: `${region.width}%`,
                  height: `${region.height}%`
                }}
              >
                <span>{region.label}</span>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ color: 'var(--muted)', fontSize: '12px' }}>
            No document loaded for preview.
          </div>
        )}
      </div>

      <div className="viewer-caption">
        <span>
          <span className="caption-dot" /> Potential manipulation signals
        </span>
        <span style={{ color: 'var(--red)', fontWeight: 600 }}>{watermark}</span>
      </div>

      {result?.tamper_analysis && (
        <TamperHeatmap tamperAnalysis={result.tamper_analysis} />
      )}
    </div>
  );
}
