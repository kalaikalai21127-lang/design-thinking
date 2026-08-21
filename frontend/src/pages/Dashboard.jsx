import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { screeningAPI } from '../services/api';
import { LayoutDashboard, CheckCircle, AlertTriangle, ShieldAlert, Activity, Plus, Download, ArrowUpRight, RefreshCw } from 'lucide-react';
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
        <p className="text-muted fw-semibold">Loading Optical Sensor Statistics...</p>
      </div>
    );
  }

  const total = stats?.total_screenings || 0;
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
            <LayoutDashboard className="text-teal-600" style={{ color: '#0d9488' }} /> Optical Jaundice Analytics Dashboard
          </h1>
          <p className="text-muted mb-0">System metrics and recorded sensor transmittance statistics.</p>
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
            <Plus size={18} /> New Sensor Screening
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
            <div className="extra-small text-muted">Recorded sensor readings</div>
          </div>
        </div>

        {/* Card 2: Normal Cases */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Normal Cases</span>
              <div className="p-2 rounded-circle bg-emerald-100 text-emerald-800" style={{ backgroundColor: '#d1fae5', color: '#065f46' }}>
                <CheckCircle size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-emerald-600 mb-1" style={{ color: '#059669' }}>{normal}</h2>
            <div className="extra-small text-muted">{total > 0 ? ((normal / total) * 100).toFixed(1) : 0}% of screenings</div>
          </div>
        </div>

        {/* Card 3: Mild Risk Cases */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">Mild Risk Cases</span>
              <div className="p-2 rounded-circle bg-amber-100 text-amber-800" style={{ backgroundColor: '#fef3c7', color: '#92400e' }}>
                <ShieldAlert size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-amber-600 mb-1" style={{ color: '#d97706' }}>{mild}</h2>
            <div className="extra-small text-muted">{total > 0 ? ((mild / total) * 100).toFixed(1) : 0}% of screenings</div>
          </div>
        </div>

        {/* Card 4: High Risk Cases */}
        <div className="col-sm-6 col-lg-3">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted extra-small text-uppercase fw-bold">High Risk Cases</span>
              <div className="p-2 rounded-circle bg-rose-100 text-rose-800" style={{ backgroundColor: '#ffe4e6', color: '#9f1239' }}>
                <AlertTriangle size={20} />
              </div>
            </div>
            <h2 className="fw-extrabold text-rose-600 mb-1" style={{ color: '#e11d48' }}>{high}</h2>
            <div className="extra-small text-muted">{total > 0 ? ((high / total) * 100).toFixed(1) : 0}% of screenings</div>
          </div>
        </div>
      </div>

      {/* Distribution Progress Bar Visualizer */}
      <div className="medical-card p-4 border-0 shadow-sm mb-5">
        <h5 className="fw-bold text-dark mb-3">Screening Risk Breakdown</h5>
        {total > 0 ? (
          <div>
            <div className="progress mb-2" style={{ height: '16px', borderRadius: '10px' }}>
              <div
                className="progress-bar bg-success"
                role="progressbar"
                style={{ width: `${(normal / total) * 100}%` }}
                title={`Normal (${normal})`}
              ></div>
              <div
                className="progress-bar bg-warning"
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
            <div className="d-flex justify-content-between small text-muted">
              <span className="d-flex align-items-center gap-1">
                <span className="d-inline-block rounded-circle bg-success" style={{ width: '10px', height: '10px' }}></span>
                Normal ({normal})
              </span>
              <span className="d-flex align-items-center gap-1">
                <span className="d-inline-block rounded-circle bg-warning" style={{ width: '10px', height: '10px' }}></span>
                Mild Risk ({mild})
              </span>
              <span className="d-flex align-items-center gap-1">
                <span className="d-inline-block rounded-circle bg-danger" style={{ width: '10px', height: '10px' }}></span>
                High Risk ({high})
              </span>
            </div>
          </div>
        ) : (
          <p className="text-muted small mb-0">No screening records available yet.</p>
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
                  <th>Patient Name</th>
                  <th>Sensor Reading</th>
                  <th>Predicted Status</th>
                  <th>Confidence</th>
                  <th>Timestamp</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {recent.map((s) => {
                  const isNorm = s.status === 'Normal';
                  const isM = s.status === 'Mild Risk';
                  return (
                    <tr key={s.id}>
                      <td className="fw-bold text-muted">#{s.id}</td>
                      <td className="fw-semibold text-dark">{s.patient_name}</td>
                      <td>
                        <span className="badge bg-dark bg-opacity-75 fs-6 px-3">{s.sensor_reading}</span>
                      </td>
                      <td>
                        <span className={`badge ${isNorm ? 'bg-success' : isM ? 'bg-warning text-dark' : 'bg-danger'}`}>
                          {s.status}
                        </span>
                      </td>
                      <td className="fw-bold text-dark">{s.confidence}%</td>
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
