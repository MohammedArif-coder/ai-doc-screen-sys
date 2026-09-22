import React from 'react';
import { ShieldCheck, ScanLine, FileCheck } from 'lucide-react';

export default function Sidebar({ page, setPage }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <ShieldCheck size={22} />
        </div>
        <div>
          <div className="brand-name">DAKSH</div>
          <div className="brand-sub">VISA AUTHENTICATOR</div>
        </div>
      </div>

      <div className="workspace-card">
        <div className="workspace-kicker">CORE TOOL</div>
        <div className="workspace-name">Tamper & Anomaly Detection</div>
        <div className="workspace-status">
          <span /> System Ready
        </div>
      </div>

      <nav>
        <button className="active">
          <ScanLine size={18} />
          <span>Visa Authenticator</span>
        </button>
      </nav>

      <div className="sidebar-bottom">
        <div className="support" style={{ borderTop: '1px solid var(--line)', paddingTop: '14px' }}>
          <ShieldCheck size={16} color="var(--green)" />
          <div>
            <strong style={{ color: 'var(--green)' }}>Authenticity Engine</strong>
            <small>AI & Image Analysis</small>
          </div>
        </div>
      </div>
    </aside>
  );
}
