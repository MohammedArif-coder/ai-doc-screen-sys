import React, { useState } from 'react';
import { ArrowUpRight, Search, Clock3, Filter } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

export default function ScreeningHistory({ history = [] }) {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');

  const filteredRows = history.filter((item) => {
    // Risk filter
    if (filter === 'low_concern' && item.risk_level !== 'low_concern') return false;
    if (filter === 'review' && item.risk_level !== 'review') return false;
    if (filter === 'high_concern' && item.risk_level !== 'high_concern') return false;

    // Search term filter
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      const matchId = (item.document_id || '').toLowerCase().includes(term);
      const matchName = (item.document_name || '').toLowerCase().includes(term);
      const matchStatus = (item.status || '').toLowerCase().includes(term);
      return matchId || matchName || matchStatus;
    }

    return true;
  });

  return (
    <div className="history-page">
      <div className="section-title">
        <div>
          <div className="eyebrow">AUDIT LOG / LOCAL SQLITE DATABASE</div>
          <h1>Screening History</h1>
          <p>Chronological record of document screening executions persisted in local prototype SQLite storage.</p>
        </div>
      </div>

      <div className="panel history-panel">
        <div className="filter-row" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', gap: '6px' }}>
            <button
              className={`filter ${filter === 'all' ? 'active' : ''}`}
              onClick={() => setFilter('all')}
            >
              All Records ({history.length})
            </button>
            <button
              className={`filter ${filter === 'low_concern' ? 'active' : ''}`}
              onClick={() => setFilter('low_concern')}
            >
              Low Concern
            </button>
            <button
              className={`filter ${filter === 'review' ? 'active' : ''}`}
              onClick={() => setFilter('review')}
            >
              Review Required
            </button>
            <button
              className={`filter ${filter === 'high_concern' ? 'active' : ''}`}
              onClick={() => setFilter('high_concern')}
            >
              High Concern
            </button>
          </div>

          <div style={{ position: 'relative', minWidth: '220px' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '10px', color: 'var(--muted)' }} />
            <input
              type="text"
              placeholder="Search by Document ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                background: '#091724',
                border: '1px solid var(--line)',
                borderRadius: '5px',
                padding: '6px 10px 6px 30px',
                fontSize: '11px',
                color: '#dce8f0'
              }}
            />
          </div>
        </div>

        <div className="table-wrap" style={{ marginTop: '14px' }}>
          <table>
            <thead>
              <tr>
                <th>Record ID</th>
                <th>Document ID</th>
                <th>Type</th>
                <th>Screening Timestamp</th>
                <th>OCR Score</th>
                <th>Consistency</th>
                <th>Image Quality</th>
                <th>Tamper Flag</th>
                <th>Risk Level</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredRows.length === 0 ? (
                <tr>
                  <td colSpan="10" style={{ textAlign: 'center', padding: '24px', color: 'var(--muted)' }}>
                    No screening history records match the selected filter.
                  </td>
                </tr>
              ) : (
                filteredRows.map((row, idx) => (
                  <tr key={idx}>
                    <td>#{row.id || idx + 1}</td>
                    <td>
                      <strong>{row.document_id}</strong>
                    </td>
                    <td>{row.document_type}</td>
                    <td>{new Date(row.screening_date).toLocaleString('en-GB')}</td>
                    <td>{row.ocr_score}%</td>
                    <td>{row.consistency_score}%</td>
                    <td>{row.image_quality}%</td>
                    <td style={{ color: row.tamper_signal ? 'var(--amber)' : 'var(--green)' }}>
                      {row.tamper_signal ? 'SIGNAL' : 'CLEAR'}
                    </td>
                    <td>
                      <StatusBadge status={row.risk_level} />
                    </td>
                    <td>{row.status}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
