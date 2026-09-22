import React from 'react';
import { Menu, ChevronRight } from 'lucide-react';

export default function Header({ onMenu, activePageLabel = 'Screening Workspace' }) {
  return (
    <header className="topbar">
      <button className="mobile-menu" onClick={onMenu} aria-label="Open Navigation">
        <Menu size={19} />
      </button>

      <div className="crumb">
        Operations <ChevronRight size={14} /> <strong>{activePageLabel}</strong>
      </div>

      <div className="top-actions">
        <span className="demo-pill">
          <span /> DEMO MODE
        </span>
        <span className="online">
          <span /> SYSTEM ONLINE
        </span>
        <div className="avatar">DS</div>
      </div>
    </header>
  );
}
