import React, { useEffect, useState } from 'react';
import { screeningAPI } from '../services/api';
import { History as HistoryIcon, Search, Trash2, Download, Eye, AlertCircle, RefreshCw } from 'lucide-react';
import ResultCard from '../components/ResultCard';

const History = () => {
  const [historyList, setHistoryList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [selectedResult, setSelectedResult] = useState(null);
  const [error, setError] = useState('');
  const [actionMsg, setActionMsg] = useState('');

  const fetchHistory = async () => {
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
    fetchHistory();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm(`Are you sure you want to delete screening record #${id}?`)) return;

    try {
      await screeningAPI.deleteRecord(id);
      setActionMsg(`Record #${id} deleted successfully.`);
      setTimeout(() => setActionMsg(''), 3000);
      fetchHistory();
    } catch (err) {
      setError(err.response?.data?.error || `Failed to delete record #${id}.`);
    }
  };

  // Search and Filter Logic
  const filteredHistory = historyList.filter((item) => {
    const matchesSearch =
      item.patient_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.status.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.sensor_reading.toString().includes(searchTerm) ||
      item.timestamp.includes(searchTerm);

    if (filterStatus === 'NORMAL') return matchesSearch && item.status === 'Normal';
    if (filterStatus === 'MILD') return matchesSearch && item.status === 'Mild Risk';
    if (filterStatus === 'HIGH') return matchesSearch && item.status === 'High Risk';
    return matchesSearch;
  });

  return (
    <div className="container py-5">
      <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center mb-4 gap-3">
        <div>
          <h1 className="fw-extrabold text-slate-900 mb-1 d-flex align-items-center gap-2">
            <HistoryIcon className="text-teal-600" style={{ color: '#0d9488' }} /> Screening History & AI Dataset
          </h1>
          <p className="text-muted mb-0">Manage stored optical sensor readings and export training dataset.</p>
        </div>

        <a
          href={screeningAPI.getExportUrl()}
          className="btn btn-medical d-flex align-items-center gap-2 shadow-sm"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Download size={18} /> Export Dataset (CSV)
        </a>
      </div>

      {actionMsg && (
        <div className="alert alert-success py-2 px-3 small mb-4 rounded-3">
          {actionMsg}
        </div>
      )}

      {error && (
        <div className="alert alert-danger py-2 px-3 small mb-4 rounded-3">
          {error}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="medical-card p-3 border-0 shadow-sm mb-4">
        <div className="row g-3 align-items-center">
          <div className="col-md-6">
            <div className="input-group">
              <span className="input-group-text bg-light border-end-0"><Search size={18} className="text-muted" /></span>
              <input
                type="text"
                className="form-control bg-light border-start-0 py-2"
                placeholder="Search patient name, status, or sensor value..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="col-md-6 d-flex justify-content-md-end gap-2">
            <div className="btn-group w-100 w-md-auto" role="group">
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
                  <th>Patient Name</th>
                  <th>Age / Gender</th>
                  <th>Sensor Reading (0-255)</th>
                  <th>Status</th>
                  <th>Confidence</th>
                  <th>Timestamp</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredHistory.map((item) => {
                  const isNorm = item.status === 'Normal';
                  const isM = item.status === 'Mild Risk';
                  return (
                    <tr key={item.id}>
                      <td className="fw-bold text-muted">#{item.id}</td>
                      <td className="fw-bold text-dark">{item.patient_name}</td>
                      <td className="small text-muted">{item.age} yrs / {item.gender}</td>
                      <td>
                        <span className="badge bg-dark bg-opacity-85 fs-6 px-3">{item.sensor_reading}</span>
                      </td>
                      <td>
                        <span className={`badge ${isNorm ? 'bg-success' : isM ? 'bg-warning text-dark' : 'bg-danger'}`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="fw-bold text-dark">{item.confidence}%</td>
                      <td className="extra-small text-muted">{item.timestamp}</td>
                      <td>
                        <div className="d-flex gap-2">
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-medical"
                            onClick={() => setSelectedResult(item)}
                          >
                            <Eye size={14} /> View
                          </button>
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-danger"
                            onClick={() => handleDelete(item.id)}
                            title="Delete Record"
                          >
                            <Trash2 size={14} />
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

export default History;
