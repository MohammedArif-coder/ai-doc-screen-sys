import { useState, useRef } from 'react'

const DOC_TYPES = [
  {
    key: 'passport',
    title: 'PASSPORT',
    subtitle: 'Identity & MRZ Data',
    accept: '.jpg,.jpeg,.png,.pdf',
    color: '#38BDF8',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="4" y="2" width="16" height="20" rx="2"/>
        <line x1="8" y1="6" x2="16" y2="6"/>
        <line x1="8" y1="10" x2="16" y2="10"/>
        <circle cx="12" cy="15.5" r="2"/>
      </svg>
    )
  },
  {
    key: 'visa',
    title: 'VISA',
    subtitle: 'Travel Authorization',
    accept: '.jpg,.jpeg,.png,.pdf',
    color: '#A5B4FC',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
      </svg>
    )
  },
  {
    key: 'aadhaar',
    title: 'AADHAAR',
    subtitle: 'Printed & Digital QR',
    accept: '.jpg,.jpeg,.png,.pdf',
    color: '#34D399',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="3" y="4" width="18" height="16" rx="2"/>
        <circle cx="9" cy="10.5" r="2.5"/>
        <path d="M15 8h2M15 12h2M7 16h10"/>
      </svg>
    )
  },
  {
    key: 'driving_licence',
    title: 'DRIVING LICENCE',
    subtitle: 'RTO Details & Validity',
    accept: '.jpg,.jpeg,.png,.pdf',
    color: '#F59E0B',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="3" y="4" width="18" height="16" rx="2"/>
        <path d="M7 15h10M7 9h4"/>
      </svg>
    )
  },
  {
    key: 'pan',
    title: 'PAN CARD',
    subtitle: 'Income Tax Identity',
    accept: '.jpg,.jpeg,.png,.pdf',
    color: '#EC4899',
    icon: (
      <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
        <rect x="3" y="4" width="18" height="16" rx="2"/>
        <line x1="7" y1="8" x2="17" y2="8"/>
        <line x1="7" y1="12" x2="13" y2="12"/>
      </svg>
    )
  }
]

function formatBytes(bytes) {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

export function UploadZone({ files, setFiles, onAnalyze, busy }) {
  const [dragOverKey, setDragOverKey] = useState(null)
  const fileInputRefs = {
    passport: useRef(null),
    visa: useRef(null),
    aadhaar: useRef(null),
    driving_licence: useRef(null),
    pan: useRef(null)
  }

  const loadedCount = [files.passport, files.visa, files.aadhaar, files.driving_licence, files.pan].filter(Boolean).length
  const hasFiles = loadedCount > 0

  const handleFileChange = (key, file) => {
    if (!file) return
    let previewUrl = null
    if (file.type.startsWith('image/')) {
      previewUrl = URL.createObjectURL(file)
    }
    setFiles(prev => ({
      ...prev,
      [key]: { file, name: file.name, size: file.size, type: file.type || 'image/jpeg', previewUrl }
    }))
  }

  const handleRemove = (key, e) => {
    e.stopPropagation()
    if (files[key]?.previewUrl) URL.revokeObjectURL(files[key].previewUrl)
    setFiles(prev => ({ ...prev, [key]: null }))
    if (fileInputRefs[key]?.current) fileInputRefs[key].current.value = ''
  }

  const handleDrop = (key, e) => {
    e.preventDefault()
    setDragOverKey(null)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(key, e.dataTransfer.files[0])
    }
  }

  return (
    <section className="upload-container panel">
      <div className="upload-header">
        <div className="upload-title-block">
          <span className="section-badge">CASE INTAKE</span>
          <h2>Start a Document Screening Case</h2>
          <p className="upload-subtitle">
            Upload identity documents for cross-document evidence analysis.
          </p>
        </div>
        <div className="upload-readiness">
          <span className={`readiness-pill ${loadedCount === 5 ? 'ready-all' : loadedCount > 0 ? 'ready-partial' : 'ready-none'}`}>
            <span className="readiness-dot"></span>
            {loadedCount === 0 ? 'No documents loaded' : `${loadedCount} of 5 documents loaded`}
          </span>
        </div>
      </div>

      <div className="upload-cards-grid">
        {DOC_TYPES.map(doc => {
          const fileData = files[doc.key]
          const isDragging = dragOverKey === doc.key

          return (
            <div
              key={doc.key}
              className={`upload-card ${fileData ? 'has-file' : ''} ${isDragging ? 'drag-over' : ''}`}
              style={fileData ? { '--card-accent': doc.color } : {}}
              onDragOver={(e) => { e.preventDefault(); setDragOverKey(doc.key) }}
              onDragLeave={() => setDragOverKey(null)}
              onDrop={(e) => handleDrop(doc.key, e)}
              onClick={() => fileInputRefs[doc.key].current?.click()}
            >
              <input
                ref={fileInputRefs[doc.key]}
                type="file"
                accept={doc.accept}
                style={{ display: 'none' }}
                onChange={(e) => handleFileChange(doc.key, e.target.files?.[0])}
              />

              {fileData ? (
                /* LOADED STATE */
                <div className="card-loaded">
                  {/* Thumbnail or PDF placeholder */}
                  <div className="card-thumb-area">
                    {fileData.previewUrl ? (
                      <img src={fileData.previewUrl} alt={doc.title} className="card-thumb-img" />
                    ) : (
                      <div className="card-thumb-pdf">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke={doc.color} strokeWidth="1.5">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                        </svg>
                        <span className="pdf-ext">PDF</span>
                      </div>
                    )}
                    {/* Overlay badge */}
                    <div className="thumb-overlay">
                      <span className="doc-type-label" style={{ color: doc.color }}>{doc.title}</span>
                    </div>
                  </div>

                  <div className="card-loaded-info">
                    <div className="loaded-status-row">
                      <span className="loaded-check">✓</span>
                      <span className="loaded-label">Ready for screening</span>
                    </div>
                    <p className="loaded-filename" title={fileData.name}>{fileData.name}</p>
                    <span className="loaded-size">{formatBytes(fileData.size)}</span>
                  </div>

                  <div className="card-loaded-actions">
                    <button
                      type="button"
                      className="btn-replace"
                      onClick={(e) => { e.stopPropagation(); fileInputRefs[doc.key].current?.click() }}
                    >
                      Replace
                    </button>
                    <button
                      type="button"
                      className="btn-remove"
                      onClick={(e) => handleRemove(doc.key, e)}
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ) : (
                /* EMPTY STATE */
                <div className="card-empty-state">
                  <div className="doc-icon-wrapper" style={{ color: doc.color, borderColor: `color-mix(in srgb, ${doc.color} 25%, transparent)` }}>
                    {doc.icon}
                  </div>
                  <h3 className="doc-type-title">{doc.title}</h3>
                  <p className="doc-subtitle">{doc.subtitle}</p>
                  <div className={`drop-zone-prompt ${isDragging ? 'dragging' : ''}`}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <span>{isDragging ? 'Drop to add' : 'Drop or browse'}</span>
                  </div>
                  <span className="file-types-label">JPG · PNG · PDF</span>
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="upload-footer">
        <div className="intake-note">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#64748B" strokeWidth="2">
            <rect x="3" y="11" width="18" height="11" rx="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <span>Upload at least 1 document. Files are processed in memory and not stored.</span>
        </div>

        <button
          type="button"
          className="btn-analyze-primary"
          disabled={!hasFiles || busy}
          onClick={onAnalyze}
        >
          {busy ? (
            <>
              <span className="spinner-icon"></span>
              Screening Case...
            </>
          ) : (
            <>
              {hasFiles
                ? `Analyze ${loadedCount === 5 ? 'All 5' : loadedCount} Document${loadedCount !== 1 ? 's' : ''}`
                : 'Analyze Case'}
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                <line x1="5" y1="12" x2="19" y2="12"/>
                <polyline points="12 5 19 12 12 19"/>
              </svg>
            </>
          )}
        </button>
      </div>
    </section>
  )
}
