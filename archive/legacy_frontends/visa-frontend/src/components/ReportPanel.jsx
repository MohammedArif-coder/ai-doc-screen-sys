import React, { useState } from 'react';
import { Download, ShieldCheck, AlertTriangle, FileCheck } from 'lucide-react';
import StatusBadge from './StatusBadge';
import { api } from '../services/api';

export default function ReportPanel({ result }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async () => {
    setDownloading(true);
    try {
      const blob = await api.generateReport(
        result || {
          document_id: 'DEMO-000123',
          status: 'review',
          findings: [{ message: 'Example synthetic finding for demonstration' }],
        }
      );
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `daksh-screening-report-${result?.document_id || 'DEMO-000123'}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(`Report download error: ${err.message}`);
    } finally {
      setDownloading(false);
    }
  };

  const docId = result?.document_id || 'DEMO-000123';
  const status = result?.status || 'review';
  const findings = result?.findings || [{ message: 'Sample signal waiting for screening run.' }];

  return (
    <div className="report-layout">
      <div className="panel report-paper">
        <div className="report-brand">
          <div className="brand-mark">
            <ShieldCheck size={20} />
          </div>
          <div>
            <strong>DAKSH</strong>
            <span>Visa Screening Report</span>
          </div>
        </div>

        <div className="report-rule" />

        <div className="report-row">
          <span>Document ID</span>
          <strong>{docId}</strong>
        </div>
        <div className="report-row">
          <span>Date</span>
          <strong>{new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</strong>
        </div>
        <div className="report-row">
          <span>Screening Result</span>
          <StatusBadge status={status} />
        </div>

        <h3>Detected Signals</h3>
        {findings.map((f, i) => (
          <div className="report-signal" key={i}>
            <AlertTriangle size={15} />
            {f.message}
          </div>
        ))}

        <div className="recommendation">
          <strong>Recommendation</strong>
          <p>
            Manual document verification is recommended. This report contains automated screening signals for human operator review and does not constitute a final legal authenticity judgment.
          </p>
        </div>

        <button className="primary-btn" onClick={handleDownload} disabled={downloading}>
          <Download size={17} />
          {downloading ? 'Generating PDF...' : 'Download PDF Report'}
        </button>
      </div>

      <div className="panel report-note">
        <div className="panel-kicker">REPORT CONTEXT & MANDATORY NOTICE</div>
        <h2>Built for Accountable Review</h2>
        <p>
          Every generated screening report carries an immutable header identifying it as a demonstration prototype record. Automated findings serve as assistive indicators for authorized screening personnel.
        </p>
        <div className="notice">
          <ShieldCheck size={16} />
          <span>FOR DEMONSTRATION / SCREENING PROTOTYPE ONLY — NOT A REAL VISA</span>
        </div>
      </div>
    </div>
  );
}
