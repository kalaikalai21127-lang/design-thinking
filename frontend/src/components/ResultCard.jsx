import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, Activity, User, Calendar } from 'lucide-react';
import RiskGauge from './RiskGauge';

const ResultCard = ({ result, onReset }) => {
  if (!result) return null;

  const isNormal = result.status === 'Normal';
  const isMild = result.status === 'Mild Risk';
  const isHigh = result.status === 'High Risk';

  let cardHeaderBg = 'bg-danger text-white';
  let badgeClass = 'bg-danger text-white';
  let icon = <AlertTriangle size={32} />;

  if (isNormal) {
    cardHeaderBg = 'bg-emerald-600 text-white';
    badgeClass = 'bg-success text-white';
    icon = <CheckCircle size={32} />;
  } else if (isMild) {
    cardHeaderBg = 'bg-warning text-dark';
    badgeClass = 'bg-warning text-dark';
    icon = <ShieldAlert size={32} />;
  }

  return (
    <div className="card border-0 shadow-lg rounded-4 overflow-hidden my-4">
      <div className={`p-4 ${cardHeaderBg}`} style={{ backgroundColor: isNormal ? '#10b981' : isMild ? '#f59e0b' : '#ef4444' }}>
        <div className="d-flex align-items-center gap-3">
          <div className="bg-white bg-opacity-20 p-3 rounded-circle">{icon}</div>
          <div>
            <h4 className="fw-bold mb-0">Screening Result Output</h4>
            <p className="mb-0 extra-small opacity-90">Optical Sensor Jaundice Assessment</p>
          </div>
        </div>
      </div>

      <div className="card-body p-4">
        <div className="row gy-4">
          <div className="col-md-6 border-end-md">
            <div className="mb-4">
              <div className="text-muted extra-small text-uppercase fw-semibold">Optical Reading Value</div>
              <div className="display-5 fw-extrabold text-dark">{result.reading || result.sensor_value}</div>
              <div className="text-muted small">Transmittance Units (0 - 255)</div>
            </div>

            <div className="row g-2 mb-3">
              <div className="col-6">
                <div className="p-3 bg-light rounded-3 border">
                  <div className="text-muted extra-small text-uppercase">Risk Status</div>
                  <div className={`fw-bold fs-5 ${isNormal ? 'text-success' : isMild ? 'text-warning' : 'text-danger'}`}>
                    {result.status}
                  </div>
                </div>
              </div>

              <div className="col-6">
                <div className="p-3 bg-light rounded-3 border">
                  <div className="text-muted extra-small text-uppercase">Confidence</div>
                  <div className="fw-bold fs-5 text-dark">{result.confidence}%</div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <h6 className="fw-bold text-dark mb-2">Patient Details</h6>
            <div className="p-3 bg-light rounded-3 border mb-3 small">
              <div className="d-flex align-items-center gap-2 mb-1">
                <User size={16} className="text-muted" />
                <span><strong>Name:</strong> {result.patient?.name || 'Anonymous Patient'}</span>
              </div>
              <div className="d-flex justify-content-between text-muted extra-small">
                <span><strong>Age:</strong> {result.patient?.age || 'N/A'} yrs</span>
                <span><strong>Gender:</strong> {result.patient?.gender || 'N/A'}</span>
              </div>
            </div>

            <h6 className="fw-bold text-dark mb-2">Clinical Recommendation</h6>
            <div className={`alert p-3 rounded-3 mb-0 small ${isNormal ? 'alert-success' : isMild ? 'alert-warning' : 'alert-danger'}`}>
              {result.recommendation}
            </div>
          </div>
        </div>

        <div className="mt-4">
          <RiskGauge value={result.reading || result.sensor_value} />
        </div>
      </div>

      {onReset && (
        <div className="card-footer bg-light p-3 text-end border-0">
          <button type="button" className="btn btn-medical" onClick={onReset}>
            Perform Another Screening
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
