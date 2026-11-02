import React, { useEffect, useState } from 'react';
import { screeningAPI } from '../services/api';
import { Clock, Search, Trash2, Download, Eye, AlertCircle, CheckCircle, ShieldAlert, AlertTriangle, RefreshCw, Cpu } from 'lucide-react';
import ResultCard from '../components/ResultCard';

const History = () => {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const loadHistory = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await screeningAPI.getHistory();
      setHistoryList(data.history || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load screening history database.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to permanently delete screening record #${id}?`)) {
      return;
    }

    try {
      await screeningAPI.deleteRecord(id);
      setSuccessMsg(`Screening record #${id} deleted successfully.`);
      setHistoryList(prev => prev.filter(item => item.id !== id));
      if (selectedRecord?.id === id) {
        setSelectedRecord(null);
      }
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to delete record.');
    }
  };

  const filteredHistory = historyList.filter(item => {
    const matchesSearch =
      item.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.sensor_type && item.sensor_type.toLowerCase().includes(searchTerm.toLowerCase()));

    if (!matchesSearch) return false;

    if (filterStatus === 'ALL') return true;
    if (filterStatus === 'CALIBRATION') return item.status === 'Calibration Required';
    if (filterStatus === 'NORMAL') return item.status === 'Normal';
    if (filterStatus === 'MILD') return item.status === 'Mild Risk';
    if (filterStatus === 'HIGH') return item.status === 'High Risk';

    return true;
  });

  return (
    <div className="container py-5">
      {/* Page Header */}
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h1 className="fw-extrabold text-slate-900 mb-1 d-flex align-items-center gap-2">
            <Clock className="text-teal-600" style={{ color: '#0d9488' }} /> AS7262 Spectral Screening History
          </h1>
          <p className="text-muted mb-0">Browse saved multi-spectral sensor records and export clinical AI dataset.</p>
        </div>

        <div className="d-flex gap-2">
          <button type="button" className="btn btn-outline-secondary d-flex align-items-center gap-2" onClick={loadHistory}>
            <RefreshCw size={16} /> Refresh
          </button>
          <a
            href={screeningAPI.getExportUrl()}
            className="btn btn-medical d-flex align-items-center gap-2 shadow-sm"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Download size={18} /> Export Dataset (CSV)
          </a>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger py-2 px-3 small mb-4 rounded-3 d-flex align-items-center gap-2">
          <AlertCircle size={18} /> {error}
        </div>
      )}

      {successMsg && (
        <div className="alert alert-success py-2 px-3 small mb-4 rounded-3 d-flex align-items-center gap-2">
          <CheckCircle size={18} /> {successMsg}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="medical-card p-3 border-0 shadow-sm mb-4">
        <div className="row g-3 align-items-center">
          <div className="col-md-5">
            <div className="input-group">
              <span className="input-group-text bg-light border-end-0"><Search size={18} className="text-muted" /></span>
              <input
                type="text"
                className="form-control bg-light border-start-0 py-2"
                placeholder="Search by name, status, or sensor..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="col-md-7 d-flex justify-content-md-end gap-2">
            <div className="btn-group w-100 w-md-auto flex-wrap" role="group">
              <button
                type="button"
                className={`btn btn-sm ${filterStatus === 'ALL' ? 'btn-teal text-white' : 'btn-outline-secondary'}`}
                style={{ backgroundColor: filterStatus === 'ALL' ? '#0d9488' : 'transparent', color: filterStatus === 'ALL' ? '#fff' : '#64748b' }}
                onClick={() => setFilterStatus('ALL')}
              >
                All ({historyList.length})
              </button>
              <button
                type="button"
                className={`btn btn-sm ${filterStatus === 'CALIBRATION' ? 'btn-warning text-dark fw-bold' : 'btn-outline-secondary'}`}
                onClick={() => setFilterStatus('CALIBRATION')}
              >
                Calibration Required
              </button>
              <button
                type="button"
                className={`btn btn-sm ${filterStatus === 'NORMAL' ? 'btn-success text-white' : 'btn-outline-secondary'}`}
                onClick={() => setFilterStatus('NORMAL')}
              >
                Normal
              </button>
              <button
                type="button"
                className={`btn btn-sm ${filterStatus === 'MILD' ? 'btn-warning text-dark fw-bold' : 'btn-outline-secondary'}`}
                onClick={() => setFilterStatus('MILD')}
              >
                Mild Risk
              </button>
              <button
                type="button"
                className={`btn btn-sm ${filterStatus === 'HIGH' ? 'btn-danger text-white' : 'btn-outline-secondary'}`}
                onClick={() => setFilterStatus('HIGH')}
              >
                High Risk
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* History Database Table */}
      <div className="medical-card p-4 border-0 shadow-sm">
        {loading ? (
          <div className="text-center py-5">
            <div className="spinner-border text-teal-600 mb-2" role="status" style={{ color: '#0d9488' }}>
              <span className="visually-hidden">Loading history...</span>
            </div>
            <p className="text-muted small">Querying Database...</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="text-center py-5 text-muted">
            <p className="mb-0">No matching screening records found.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover align-middle mb-0">
              <thead className="table-light extra-small text-uppercase text-muted">
                <tr>
                  <th>#ID</th>
                  <th>Subject Name</th>
                  <th>Age / Gender</th>
                  <th>Sensor Type</th>
                  <th>Violet (450nm)</th>
                  <th>Green (550nm)</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((item) => {
                  const isCalib = item.status === 'Calibration Required';
                  const isNorm = item.status === 'Normal';
                  const isM = item.status === 'Mild Risk';
                  const ch = item.channels || {};
                  return (
                    <tr key={item.id}>
                      <td className="fw-bold text-muted">#{item.id}</td>
                      <td className="fw-bold text-dark">{item.patient_name}</td>
                      <td className="small text-muted">{item.age} / {item.gender}</td>
                      <td>
                        <span className="badge bg-secondary">{item.sensor_type || 'AS7262'}</span>
                      </td>
                      <td>
                        {ch.violet !== undefined && ch.violet !== null ? (
                          <span className="badge" style={{ background: '#ede9fe', color: '#6d28d9' }}>
                            {ch.violet}
                          </span>
                        ) : (
                          <span className="extra-small text-muted">{item.sensor_reading}</span>
                        )}
                      </td>
                      <td>
                        {ch.green !== undefined && ch.green !== null ? (
                          <span className="badge" style={{ background: '#dcfce7', color: '#15803d' }}>
                            {ch.green}
                          </span>
                        ) : (
                          <span className="extra-small text-muted">-</span>
                        )}
                      </td>
                      <td>
                        <span className={`badge ${isCalib ? 'bg-warning text-dark' : isNorm ? 'bg-success' : isM ? 'bg-info text-dark' : 'bg-danger'}`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="small text-muted">{item.timestamp}</td>
                      <td>
                        <div className="d-flex gap-1">
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-medical py-1 px-2"
                            title="View Full Spectral Report"
                            onClick={() => setSelectedRecord(item)}
                          >
                            <Eye size={15} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-danger py-1 px-2"
                            title="Delete Record"
                            onClick={() => handleDelete(item.id)}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedRecord && (
        <div className="modal fade show d-block backdrop-blur" style={{ backgroundColor: 'rgba(15,23,42,0.65)' }}>
          <div className="modal-dialog modal-dialog-centered modal-lg">
            <div className="modal-content border-0 shadow-lg rounded-4 overflow-hidden">
              <div className="modal-header border-0 pb-0">
                <button type="button" className="btn-close" onClick={() => setSelectedRecord(null)}></button>
              </div>
              <div className="modal-body p-4">
                <ResultCard result={selectedRecord} onReset={() => setSelectedRecord(null)} />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default History;
