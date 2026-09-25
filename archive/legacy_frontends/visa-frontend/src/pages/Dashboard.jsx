import React from 'react';
import {
  FileSearch,
  AlertTriangle,
  CheckCircle2,
  Gauge,
  ScanLine,
  FolderOpen,
  ArrowUpRight,
  Sparkles,
  ShieldCheck,
  FileText,
  Activity,
  Layers,
  Lock
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export default function Dashboard({ setPage, history = [] }) {
  const suspiciousCount = history.filter((x) => x.risk_level === 'high_concern').length;
  const lowRiskCount = history.filter((x) => x.risk_level === 'low_concern').length;
  const reviewCount = history.filter((x) => x.risk_level === 'review').length;
  const totalCount = history.length || 24;

  const chartData = [
    { name: 'Low Concern', value: lowRiskCount || 14, color: 'var(--green)' },
    { name: 'Review Required', value: reviewCount || 6, color: 'var(--amber)' },
    { name: 'High Suspicion', value: suspiciousCount || 4, color: 'var(--red)' },
  ];

  return (
    <div className="dashboard-page">
      {/* Landing Experience Hero Banner */}
      <div
        className="hero-banner"
        style={{
          background: 'linear-gradient(135deg, #0d2334 0%, #081622 100%)',
          border: '1px solid #1c3d54',
          borderRadius: '10px',
          padding: '28px 32px',
          marginBottom: '24px',
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div className="eyebrow" style={{ color: '#8cdbf4', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ShieldCheck size={16} /> AI-ASSISTED SCREENING PROTOTYPE
            </div>
            <h1 style={{ fontFamily: 'Space Grotesk', fontSize: '28px', color: '#f0f7f9', margin: '8px 0 6px' }}>
              DAKSH — Document Authentication & Screening Hub
            </h1>
            <p style={{ color: '#89a2b3', fontSize: '13px', maxWidth: '640px', margin: 0 }}>
              Prototype system for authorized document screeners to analyze synthetic visas for inconsistencies, image manipulation, missing fields, suspicious formatting, and OCR mismatches.
            </p>

            <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
              <button className="primary-btn" onClick={() => setPage('screening')}>
                <ScanLine size={17} /> START VISA SCREENING
              </button>
              <button className="secondary-btn" onClick={() => setPage('demos')} style={{ marginTop: 0 }}>
                <FolderOpen size={17} /> VIEW DEMO DOCUMENTS
              </button>
            </div>
          </div>
        </div>

        {/* 5 Key Capabilities Pills */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '10px',
            marginTop: '24px',
            paddingTop: '20px',
            borderTop: '1px solid #193549'
          }}
        >
          {[
            { icon: FileText, label: 'OCR Analysis' },
            { icon: Activity, label: 'Image Analysis' },
            { icon: Layers, label: 'Consistency Checking' },
            { icon: AlertTriangle, label: 'Tampering Signals' },
            { icon: ShieldCheck, label: 'Screening Reports' },
          ].map((item, idx) => {
            const Icon = item.icon;
            return (
              <div
                key={idx}
                style={{
                  background: '#091b29',
                  border: '1px solid #1a354a',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  fontSize: '11px',
                  color: '#b5cbd8'
                }}
              >
                <Icon size={14} color="#5caecb" />
                <span>{item.label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Metrics Row */}
      <div className="metrics">
        <div className="metric">
          <div className="metric-icon blue">
            <FileSearch size={18} />
          </div>
          <div>
            <div className="metric-label">Total Documents Screened</div>
            <div className="metric-value">{totalCount}</div>
            <div className="metric-trend">↑ 100% synthetic baseline</div>
          </div>
        </div>

        <div className="metric">
          <div className="metric-icon red">
            <AlertTriangle size={18} />
          </div>
          <div>
            <div className="metric-label">Potentially Suspicious</div>
            <div className="metric-value">{suspiciousCount || '04'}</div>
            <div className="metric-trend">High concern signals</div>
          </div>
        </div>

        <div className="metric">
          <div className="metric-icon green">
            <CheckCircle2 size={18} />
          </div>
          <div>
            <div className="metric-label">Low Risk</div>
            <div className="metric-value">{lowRiskCount || '14'}</div>
            <div className="metric-trend">Consistent baseline</div>
          </div>
        </div>

        <div className="metric">
          <div className="metric-icon amber">
            <Gauge size={18} />
          </div>
          <div>
            <div className="metric-label">Manual Review Required</div>
            <div className="metric-value">{reviewCount || '06'}</div>
            <div className="metric-trend">Assigned to operator</div>
          </div>
        </div>
      </div>

      {/* Dashboard Main Grid */}
      <div className="dashboard-grid">
        {/* Recent Screening Table */}
        <div className="panel recent-panel">
          <div className="panel-head">
            <div>
              <div className="panel-kicker">LIVE SCREENING QUEUE</div>
              <h2>Recent Screenings</h2>
            </div>
            <button className="text-btn" onClick={() => setPage('history')}>
              View full audit history <ArrowUpRight size={15} />
            </button>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Document ID</th>
                  <th>Type</th>
                  <th>Screening Date</th>
                  <th>Risk Level</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {(history.length > 0
                  ? history.slice(0, 5)
                  : [
                      {
                        document_id: 'DMS-001',
                        document_type: 'Demo Visa A',
                        screening_date: '2026-09-20T14:10:00',
                        risk_level: 'low_concern',
                        status: 'Passed',
                      },
                      {
                        document_id: 'DMS-002',
                        document_type: 'Demo Visa B',
                        screening_date: '2026-09-20T13:45:00',
                        risk_level: 'review',
                        status: 'Manual Review',
                      },
                      {
                        document_id: 'DMS-003',
                        document_type: 'Demo Visa C',
                        screening_date: '2026-09-20T12:30:00',
                        risk_level: 'high_concern',
                        status: 'Review Required',
                      },
                    ]
                ).map((row, index) => (
                  <tr key={`${row.document_id}-${index}`}>
                    <td>
                      <strong>{row.document_id}</strong>
                    </td>
                    <td>{row.document_type || 'Synthetic Permit'}</td>
                    <td>{new Date(row.screening_date).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' })}</td>
                    <td>
                      <StatusBadge status={row.risk_level} />
                    </td>
                    <td>{row.status}</td>
                    <td>
                      <button className="icon-btn" onClick={() => setPage('screening')} title="Open in Screening">
                        <ArrowUpRight size={15} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Signal Distribution Donut Chart */}
        <div className="panel signal-panel">
          <div className="panel-kicker">SIGNAL DISTRIBUTION</div>
          <h2>Screening Signal Mix</h2>

          <div style={{ height: '180px', marginTop: '12px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={chartData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ background: '#091825', border: '1px solid #1f3b52', borderRadius: '6px', fontSize: '11px' }}
                  itemStyle={{ color: '#dce8f0' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="legend" style={{ marginTop: '10px' }}>
            {chartData.map((item, idx) => (
              <div key={idx}>
                <span className="legend-dot" style={{ backgroundColor: item.color }} />
                <span>{item.name}</span>
                <b>{item.value} records</b>
              </div>
            ))}
          </div>

          <div className="notice" style={{ marginTop: '16px' }}>
            <Sparkles size={16} />
            <span>All records use synthetic demo test cases. Screening signals assist human review.</span>
          </div>
        </div>
      </div>
    </div>
  );
}
