import React, { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import VisaScreening from './pages/VisaScreening';
import { api } from './services/api';

export default function App() {
  const [demos, setDemos] = useState([]);
  const [analysisResult, setAnalysisResult] = useState(null);

  useEffect(() => {
    api.getDemos()
      .then(setDemos)
      .catch((err) => console.log('Demo list warning:', err));
  }, [analysisResult]);

  return (
    <div className="app-shell">
      <Sidebar />

      <main className="main">
        <Header activePageLabel="Visa Authenticity & Tamper Detection" />

        <div className="content">
          <VisaScreening
            demos={demos}
            result={analysisResult}
            setResult={setAnalysisResult}
          />
        </div>

        <footer>
          <span>DAKSH v1.0 · Visa Document Authenticator & Tamper Detection Engine</span>
          <span>100% Focused Authenticity Score (90-100% Original / Tampered Anomaly Detection)</span>
        </footer>
      </main>
    </div>
  );
}
