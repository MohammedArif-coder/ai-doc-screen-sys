import React, { useRef, useState } from 'react';
import { UploadCloud, FolderOpen, AlertCircle, FileCheck } from 'lucide-react';

export default function UploadZone({ onFileSelected, onSelectDemo, loading }) {
  const [dragOver, setDragOver] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      processFile(file);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = (file) => {
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      alert('Please upload a valid PNG or JPG document image.');
      return;
    }
    setSelectedFileName(file.name);
    onFileSelected(file);
  };

  return (
    <div
      className={`panel upload-panel ${dragOver ? 'drag-active' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="upload-icon">
        <UploadCloud size={28} />
      </div>

      <h2>Drag & Drop Visa Document</h2>
      <p>Supports PNG, JPG, JPEG images up to 10MB.</p>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept="image/png, image/jpeg, image/jpg"
        style={{ display: 'none' }}
      />

      <div className="upload-actions" style={{ display: 'flex', gap: '10px', justifyContent: 'center', margin: '14px 0' }}>
        <button
          type="button"
          className="primary-btn"
          onClick={() => fileInputRef.current?.click()}
          disabled={loading}
        >
          <UploadCloud size={16} /> Browse Files
        </button>

        <button
          type="button"
          className="secondary-btn"
          onClick={onSelectDemo}
          disabled={loading}
          style={{ marginTop: 0 }}
        >
          <FolderOpen size={16} /> Use Demo Visa
        </button>
      </div>

      {selectedFileName && (
        <div style={{ marginTop: '12px', fontSize: '11px', color: 'var(--green)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px' }}>
          <FileCheck size={14} /> Selected: {selectedFileName}
        </div>
      )}
    </div>
  );
}
