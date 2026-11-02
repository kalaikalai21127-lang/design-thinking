import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { screeningAPI } from '../services/api';
import { LayoutDashboard, CheckCircle, AlertTriangle, ShieldAlert, Activity, Plus, Download, ArrowUpRight, Cpu } from 'lucide-react';
import ResultCard from '../components/ResultCard';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedResult, setSelectedResult] = useState(null);
  const [error, setError] = useState('');

  const fetchStats = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await screeningAPI.getStatistics();
      setStats(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch dashboard statistics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="container py-5 text-center my-auto">
        <div className="spinner-border text-teal-600 mb-3" role="status" style={{ width: '3rem', height: '3rem', color: '#0d9488' }}>
          <span className="visually-hidden">Loading Dashboard...</span>
        </div>
        <p className="text-muted fw-semibold">Loading Spectral Sensor Statistics...</p>
      </div>
    );
  }

  const total = stats?.total_screenings || 0;
  const calibReq = stats?.calibration_required_cases || 0;
  const normal = stats?.normal_cases || 0;
  const mild = stats?.mild_cases || 0;
  const high = stats?.high_cases || 0;
  const recent = stats?.recent_screenings || [];

  return (
    <div className="container py-5">
      {/* Top Action Header */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h1 className="fw-extrabold text-slate-900 mb-1 d-flex align-items-center gap-2">
            <LayoutDashboard className="text-teal-600" style={{ color: '#0d9488' }} /> AS7262 Spectral Analytics Dashboard
          </h1>
          <p className="text-muted mb-0">Multi-spectral screening logs, prototype calibration status, and dataset metrics.</p>
        </div>

        <div className="d-flex gap-2">
          <a
            href={screeningAPI.getExportUrl()}
            className="btn btn-outline-medical d-flex align-items-center gap-2"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Download size={18} /> Export Dataset (CSV)
          </a>
          <Link to="/screening" className="btn btn-medical d-flex align-items-center gap-2 shadow-sm">
            <Plus size={18} /> New Spectral Scan
          </Link>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger py-2 px-3 small mb-4 rounded-3">
          {error}
        </div>
      )}

      {/* 4 Feature Metric Cards */}
      <div className="row g-3 mb-5">
        {/* Card 1: Total Screenings */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Total Screenings</span>
              <div className="p-2 rounded-circle bg-teal-100 text-teal-800" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
                <Activity size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-dark mb-1">{total}</h2>
            <div className="extra-small text-muted">Recorded spectral scans</div>
          </div>
        </div>

        {/* Card 2: Calibration Required */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Calibration Required</span>
              <div className="p-2 rounded-circle bg-amber-100 text-amber-800" style={{ backgroundColor: '#fef3c7', color: '#92400e' }}>
                <Cpu size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-amber-600 mb-1" style={{ color: '#d97706' }}>{calibReq}</h2>
            <div className="extra-small text-muted">{total > 0 ? ((calibReq / total) * 100).toFixed(1) : 0}% uncalibrated prototype scans</div>
          </div>
        </div>

        {/* Card 3: Normal Cases */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Normal Cases</span>
              <div className="p-2 rounded-circle bg-emerald-100 text-emerald-800" style={{ backgroundColor: '#d1fae5', color: '#065f46' }}>
                <CheckCircle size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-emerald-600 mb-1" style={{ color: '#059669' }}>{normal}</h2>
            <div className="extra-small text-muted">{total > 0 ? ((normal / total) * 100).toFixed(1) : 0}% legacy/calibrated</div>
          </div>
        </div>

        {/* Card 4: Flagged Risk */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Flagged Risk Cases</span>
              <div className="p-2 rounded-circle bg-rose-100 text-rose-800" style={{ backgroundColor: '#ffe4e6', color: '#9f1239' }}>
                <AlertTriangle size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-rose-600 mb-1" style={{ color: '#e11d48' }}>{mild + high}</h2>
            <div className="extra-small text-muted">{total > 0 ? (((mild + high) / total) * 100).toFixed(1) : 0}% mild / high risk</div>
          </div>
        </div>
      </div>

      {/* Distribution Progress Bar Visualizer */}
      <div className="medical-card p-4 border-0 shadow-sm mb-5">
        <h5 className="fw-bold text-dark mb-3">Status Breakdown</h5>
        {total > 0 ? (
          <div>
            <div className="progress mb-2" style={{ height: '16px', borderRadius: '10px' }}>
              <div
                className="progress-bar bg-warning"
                role="progressbar"
                style={{ width: `${(calibReq / total) * 100}%` }}
                title={`Calibration Required (${calibReq})`}
              ></div>
              <div
                className="progress-bar bg-success"
                role="progressbar"
                style={{ width: `${(normal / total) * 100}%` }}
                title={`Normal (${normal})`}
              ></div>
              <div
                className="progress-bar bg-info"
                role="progressbar"
                style={{ width: `${(mild / total) * 100}%` }}
                title={`Mild Risk (${mild})`}
              ></div>
              <div
                className="progress-bar bg-danger"
                role="progressbar"
                style={{ width: `${(high / total) * 100}%` }}
                title={`High Risk (${high})`}
              ></div>
            </div>
            <div className="d-flex justify-content-between extra-small text-muted mt-2">
              <span><i className="bi bi-circle-fill text-warning me-1"></i> Calibration Required: {calibReq}</span>
              <span><i className="bi bi-circle-fill text-success me-1"></i> Normal: {normal}</span>
              <span><i className="bi bi-circle-fill text-info me-1"></i> Mild Risk: {mild}</span>
              <span><i className="bi bi-circle-fill text-danger me-1"></i> High Risk: {high}</span>
            </div>
          </div>
        ) : (
          <p className="text-muted small mb-0">No screenings recorded yet.</p>
        )}
      </div>

      {/* Recent Activity Table */}
      <div className="medical-card p-4 border-0 shadow-sm">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <h5 className="fw-bold text-dark mb-0">Recent Sensor Screenings</h5>
          <Link to="/history" className="text-teal-600 fw-semibold text-decoration-none small d-flex align-items-center gap-1" style={{ color: '#0d9488' }}>
            View Full History <ArrowUpRight size={16} />
          </Link>
        </div>

        {recent.length === 0 ? (
          <p className="text-muted small text-center py-4 mb-0">No recent screening logs.</p>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light extra-small text-uppercase text-muted">
                <tr>
                  <th>#ID</th>
                  <th>Subject Name</th>
                  <th>Sensor Type</th>
                  <th>Channels Preview (V, G)</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s) => {
                  const isCalib = s.status === 'Calibration Required';
                  const isNorm = s.status === 'Normal';
                  const isM = s.status === 'Mild Risk';
                  const ch = s.channels || {};
                  return (
                    <tr key={s.id}>
                      <td className="fw-bold text-muted">#{s.id}</td>
                      <td className="fw-semibold text-dark">{s.patient_name}</td>
                      <td>
                        <span className="badge bg-secondary">{s.sensor_type || 'AS7262'}</span>
                      </td>
                      <td>
                        {ch.violet !== undefined && ch.violet !== null ? (
                          <span className="font-monospace extra-small">
                            V: {ch.violet} | G: {ch.green}
                          </span>
                        ) : (
                          <span className="font-monospace extra-small text-muted">
                            Reading: {s.sensor_reading}
                          </span>
                        )}
                      </td>
                      <td>
                        <span className={`badge ${isCalib ? 'bg-warning text-dark' : isNorm ? 'bg-success' : isM ? 'bg-info text-dark' : 'bg-danger'}`}>
                          {s.status}
                        </span>
                      </td>
                      <td className="small text-muted">{s.timestamp}</td>
                      <td>
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-medical"
                          onClick={() => setSelectedResult(s)}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedResult && (
        <div className="modal fade show d-block backdrop-blur" style={{ backgroundColor: 'rgba(15,23,42,0.65)' }}>
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
              <div className="modal-header border-0 pb-0">
                <button type="button" className="btn-close" onClick={() => setSelectedResult(null)}></button>
              </div>
              <div className="modal-body p-4">
                <ResultCard result={selectedResult} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
