import React, { useState } from 'react';
import { Settings as SettingsIcon, ShieldCheck, Database, Sliders } from 'lucide-react';

export default function Settings() {
  const [demoMode, setDemoMode] = useState(true);
  const [showReminder, setShowReminder] = useState(true);
  const [autoSaveHistory, setAutoSaveHistory] = useState(true);

  return (
    <div className="settings-page">
      <div className="section-title">
        <div>
          <div className="eyebrow">CONFIGURATION / ENVIRONMENT</div>
          <h1>System Settings</h1>
          <p>Prototype controls and preferences for the local visa document screening hub.</p>
        </div>
      </div>

      <div className="panel settings-panel">
        <div className="setting">
          <div>
            <strong>Demo Mode Enabled</strong>
            <p>Keep synthetic-only test cases (DEMO-01 to DEMO-05) active in the document selector library.</p>
          </div>
          <div
            className={`toggle ${demoMode ? 'on' : ''}`}
            onClick={() => setDemoMode(!demoMode)}
            style={{ cursor: 'pointer' }}
          >
            <span />
          </div>
        </div>

        <div className="setting">
          <div>
            <strong>Human Review Reminder</strong>
            <p>Display compulsory manual verification notice on every screening result banner and generated PDF report.</p>
          </div>
          <div
            className={`toggle ${showReminder ? 'on' : ''}`}
            onClick={() => setShowReminder(!showReminder)}
            style={{ cursor: 'pointer' }}
          >
            <span />
          </div>
        </div>

        <div className="setting">
          <div>
            <strong>SQLite Audit Log Retention</strong>
            <p>Automatically log all screening runs into local SQLite database table (`daksh.db`).</p>
          </div>
          <div
            className={`toggle ${autoSaveHistory ? 'on' : ''}`}
            onClick={() => setAutoSaveHistory(!autoSaveHistory)}
            style={{ cursor: 'pointer' }}
          >
            <span />
          </div>
        </div>

        <div className="setting">
          <div>
            <strong>Storage Location</strong>
            <p>Prototype SQLite database instance running locally on host machine.</p>
          </div>
          <span className="setting-value">LOCAL SQLITE (`daksh.db`)</span>
        </div>

        <div className="setting">
          <div>
            <strong>Safety & Compliance Notice</strong>
            <p>System strictly uses synthetic fictional documents for testing software screening logic.</p>
          </div>
          <span className="setting-value" style={{ color: 'var(--amber)' }}>DEMO PROTOTYPE ONLY</span>
        </div>
      </div>
    </div>
  );
}
