import React from 'react';

const RiskGauge = ({ value }) => {
  const numVal = parseInt(value, 10) || 0;
  const percentage = Math.min(100, Math.max(0, (numVal / 255) * 100));

  let statusLabel = 'High Risk';
  let statusColorClass = 'bg-danger';
  let badgeStyle = { backgroundColor: '#ef4444', color: '#fff' };

  if (numVal >= 100) {
    statusLabel = 'Normal';
    statusColorClass = 'bg-success';
    badgeStyle = { backgroundColor: '#10b981', color: '#fff' };
  } else if (numVal >= 70) {
    statusLabel = 'Mild Risk';
    statusColorClass = 'bg-warning';
    badgeStyle = { backgroundColor: '#f59e0b', color: '#000' };
  }

  return (
    <div className="p-3 bg-light rounded-3 border">
      <div className="d-flex justify-content-between align-items-center mb-2">
        <span className="small text-muted fw-semibold">Optical Sensor Reading Spectrum (0 - 255)</span>
        <span className="badge px-3 py-1 fw-bold rounded-pill" style={badgeStyle}>
          {statusLabel} ({numVal})
        </span>
      </div>

      <div className="progress position-relative overflow-visible mb-2" style={{ height: '16px', borderRadius: '10px' }}>
        <div
          className={`progress-bar progress-bar-striped progress-bar-animated ${statusColorClass}`}
          role="progressbar"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>

      <div className="d-flex justify-content-between extra-small text-muted">
        <span>0 (High Risk: &lt; 70)</span>
        <span>70 (Mild Risk: 70 - 99)</span>
        <span>100 - 255 (Normal)</span>
      </div>
    </div>
  );
};

export default RiskGauge;
