import React from 'react';
import { AlertTriangle, CheckCircle, ShieldAlert, Activity, User, Calendar, Cpu } from 'lucide-react';
import RiskGauge from './RiskGauge';

const ResultCard = ({ result, onReset }) => {
  if (!result) return null;

  const isCalibReq = result.status === 'Calibration Required';
  const isNormal = result.status === 'Normal';
  const isMild = result.status === 'Mild Risk';
  const isHigh = result.status === 'High Risk';

  let cardHeaderBg = 'bg-warning text-dark';
  let badgeClass = 'bg-warning text-dark';
  let icon = <Activity size={32} />;

  if (isCalibReq) {
    cardHeaderBg = 'bg-amber-500 text-dark';
    badgeClass = 'bg-warning text-dark';
    icon = <Cpu size={32} />;
  } else if (isNormal) {
    cardHeaderBg = 'bg-emerald-600 text-white';
    badgeClass = 'bg-success text-white';
    icon = <CheckCircle size={32} />;
  } else if (isMild) {
    cardHeaderBg = 'bg-warning text-dark';
    badgeClass = 'bg-warning text-dark';
    icon = <ShieldAlert size={32} />;
  } else if (isHigh) {
    cardHeaderBg = 'bg-danger text-white';
    badgeClass = 'bg-danger text-white';
    icon = <AlertTriangle size={32} />;
  }

  const channels = result.channels || {
    violet: result.violet,
    blue: result.blue,
    green: result.green,
    yellow: result.yellow,
    orange: result.orange,
    red: result.red
  };

  const hasSpectralChannels = channels.violet !== undefined && channels.violet !== null;

  return (
    <div className="card border-0 shadow-lg rounded-4 overflow-hidden my-4">
      <div className={`p-4 ${cardHeaderBg}`} style={{ backgroundColor: isCalibReq ? '#f59e0b' : isNormal ? '#10b981' : isMild ? '#f97316' : '#ef4444' }}>
        <div className="d-flex align-items-center justify-content-between">
          <div className="d-flex align-items-center gap-3">
            <div className="bg-white bg-opacity-25 p-3 rounded-circle text-white">{icon}</div>
            <div>
              <h4 className="fw-bold mb-0 text-white">AS7262 Spectral Screening Output</h4>
              <p className="mb-0 extra-small text-white opacity-90">
                {isCalibReq ? 'Experimental Prototype - Clinical Calibration Required' : 'Multi-Spectral Assessment'}
              </p>
            </div>
          </div>
          <span className="badge bg-white text-dark py-2 px-3 fw-bold rounded-pill shadow-sm">
            {result.sensor_type || 'AS7262'}
          </span>
        </div>
      </div>

      <div className="card-body p-4">
        {/* Research / Safety Alert */}
        <div className="alert alert-warning border-0 rounded-3 p-3 small mb-4 d-flex align-items-start gap-2">
          <AlertTriangle size={20} className="text-warning flex-shrink-0 mt-1" />
          <div>
            <strong>Prototype Status:</strong> This is a low-cost screening prototype, not a clinically certified medical device.
            Uncalibrated spectral readings cannot diagnose jaundice without laboratory Serum Total Bilirubin (STB) calibration.
          </div>
        </div>

        <div className="row gy-4">
          <div className="col-md-6 border-end-md">
            {hasSpectralChannels ? (
              <div className="mb-4">
                <div className="text-muted extra-small text-uppercase fw-semibold mb-2">
                  AS7262 Six Calibrated Spectral Channels (&mu;W/cm&sup2;)
                </div>
                <div className="row g-2">
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#ede9fe', borderColor: '#ddd6fe' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#6d28d9' }}>450nm Violet</span>
                      <strong className="fs-5">{channels.violet}</strong>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#dbeafe', borderColor: '#bfdbfe' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#1d4ed8' }}>500nm Blue</span>
                      <strong className="fs-5">{channels.blue}</strong>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#dcfce7', borderColor: '#bbf7d0' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#15803d' }}>550nm Green</span>
                      <strong className="fs-5">{channels.green}</strong>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#fef9c3', borderColor: '#fef08a' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#a16207' }}>570nm Yellow</span>
                      <strong className="fs-5">{channels.yellow}</strong>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#ffedd5', borderColor: '#fed7aa' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#c2410c' }}>600nm Orange</span>
                      <strong className="fs-5">{channels.orange}</strong>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 border rounded text-center" style={{ background: '#fee2e2', borderColor: '#fecaca' }}>
                      <span className="extra-small d-block fw-bold" style={{ color: '#b91c1c' }}>650nm Red</span>
                      <strong className="fs-5">{channels.red}</strong>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="mb-4">
                <div className="text-muted extra-small text-uppercase fw-semibold">Optical Reading Value</div>
                <div className="display-5 fw-extrabold text-dark">{result.reading || result.sensor_value}</div>
                <div className="text-muted small">Legacy Transmittance Units (0 - 255)</div>
              </div>
            )}

            <div className="row g-2 mb-3">
              <div className="col-6">
                <div className="p-3 bg-light rounded-3 border">
                  <div className="text-muted extra-small text-uppercase">Screening Status</div>
                  <div className={`fw-bold fs-6 ${isCalibReq ? 'text-warning' : isNormal ? 'text-success' : isMild ? 'text-warning' : 'text-danger'}`}>
                    {result.status}
                  </div>
                </div>
              </div>

              <div className="col-6">
                <div className="p-3 bg-light rounded-3 border">
                  <div className="text-muted extra-small text-uppercase">Calibration Confidence</div>
                  <div className="fw-bold fs-6 text-dark">
                    {isCalibReq ? 'Pending STB Ref' : `${result.confidence}%`}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-md-6">
            <h6 className="fw-bold text-dark mb-2">Subject Demographics</h6>
            <div className="p-3 bg-light rounded-3 border mb-3 small">
              <div className="d-flex align-items-center gap-2 mb-1">
                <User size={16} className="text-muted" />
                <span><strong>Name / ID:</strong> {result.patient?.name || 'Anonymous Patient'}</span>
              </div>
              <div className="d-flex justify-content-between text-muted extra-small">
                <span><strong>Age:</strong> {result.patient?.age || '0'} days/hrs</span>
                <span><strong>Gender:</strong> {result.patient?.gender || 'N/A'}</span>
              </div>
            </div>

            <h6 className="fw-bold text-dark mb-2">Technical & Clinical Recommendation</h6>
            <div className={`alert p-3 rounded-3 mb-0 small ${isCalibReq ? 'alert-warning' : isNormal ? 'alert-success' : isMild ? 'alert-warning' : 'alert-danger'}`}>
              {result.recommendation}
            </div>
          </div>
        </div>

        {!hasSpectralChannels && (
          <div className="mt-4">
            <RiskGauge value={result.reading || result.sensor_value} />
          </div>
        )}
      </div>

      {onReset && (
        <div className="card-footer bg-light p-3 text-end border-0">
          <button type="button" className="btn btn-medical" onClick={onReset}>
            Perform Another Spectral Scan
          </button>
        </div>
      )}
    </div>
  );
};

export default ResultCard;
