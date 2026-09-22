import React from 'react';

export default function ScoreCard({ title, score, tone = 'blue', subtitle, statusLabel }) {
  const numericScore = typeof score === 'number' ? Math.max(0, Math.min(100, score)) : 0;
  
  const getProgressColor = () => {
    if (tone === 'green' || numericScore >= 80) return 'var(--green)';
    if (tone === 'amber' || (numericScore >= 55 && numericScore < 80)) return 'var(--amber)';
    if (tone === 'red' || numericScore < 55) return 'var(--red)';
    return 'var(--blue)';
  };

  return (
    <div className="score">
      <span>{title}</span>
      <strong>{score !== undefined ? `${numericScore}%` : 'N/A'}</strong>
      <div className="progress">
        <i style={{ width: `${numericScore}%`, backgroundColor: getProgressColor() }} />
      </div>
      {statusLabel && (
        <small className={numericScore < 60 ? 'text-amber' : 'text-green'}>
          {statusLabel}
        </small>
      )}
      {subtitle && <small>{subtitle}</small>}
    </div>
  );
}
