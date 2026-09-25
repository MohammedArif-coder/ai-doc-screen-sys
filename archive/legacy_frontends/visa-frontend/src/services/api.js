const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

export const api = {
  async getHealth() {
    const response = await fetch(`${API_BASE}/health`);
    if (!response.ok) throw new Error('Backend offline');
    return response.json();
  },

  async getDemos() {
    const response = await fetch(`${API_BASE}/demo/documents`);
    if (!response.ok) throw new Error('Failed to load demo documents');
    return response.json();
  },

  async getDemoDetail(id) {
    const response = await fetch(`${API_BASE}/demo/documents/${id}`);
    if (!response.ok) throw new Error('Failed to fetch demo metadata');
    return response.json();
  },

  async getHistory() {
    const response = await fetch(`${API_BASE}/visa/history`);
    if (!response.ok) throw new Error('Failed to load screening history');
    return response.json();
  },

  async analyzeDemo(documentId) {
    const response = await fetch(`${API_BASE}/visa/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ document_id: documentId })
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Demo document analysis failed');
    }
    return response.json();
  },

  async upload(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await fetch(`${API_BASE}/visa/upload`, {
      method: 'POST',
      body: formData
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Document upload failed');
    }
    return response.json();
  },

  async analyzeUpload(uploadId, fallbackText = '') {
    const response = await fetch(`${API_BASE}/visa/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ upload_id: uploadId, fallback_text: fallbackText })
    });
    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error || 'Uploaded document analysis failed');
    }
    return response.json();
  },

  async generateReport(analysisResult) {
    const response = await fetch(`${API_BASE}/reports/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(analysisResult)
    });
    if (!response.ok) throw new Error('Report generation failed');
    return response.blob();
  },

  imageUrl(path) {
    if (!path) return '';
    if (path.startsWith('http')) return path;
    const baseHost = API_BASE.replace('/api', '');
    return `${baseHost}${path}`;
  }
};
