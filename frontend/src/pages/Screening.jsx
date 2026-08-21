import React, { useState } from 'react';
import { screeningAPI } from '../services/api';
import ResultCard from '../components/ResultCard';
import RiskGauge from '../components/RiskGauge';
import { PlayCircle, Sliders, User, AlertCircle, RefreshCw, Zap } from 'lucide-react';

const Screening = () => {
  const [sensorValue, setSensorValue] = useState(120);
  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const val = parseInt(sensorValue, 10);
    if (isNaN(val) || val < 0 || val > 255) {
      setError('Sensor reading must be a valid integer between 0 and 255.');
      return;
    }

    setLoading(true);

    try {
      const data = await screeningAPI.predict(val, name, age, gender);
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process optical sensor screening.');
    } finally {
      setLoading(false);
    }
  };

  const setPreset = (val) => {
    setSensorValue(val);
    setResult(null);
  };

  const simulateRandomHardwareScan = () => {
    const randomVal = Math.floor(Math.random() * 256);
    setSensorValue(randomVal);
    setResult(null);
  };

  const handleReset = () => {
    setResult(null);
    setSensorValue(120);
    setError('');
  };

  return (
    <div className="container py-5">
      <div className="text-center max-w-2xl mx-auto mb-5">
        <span className="badge bg-teal-100 text-teal-800 py-2 px-3 rounded-pill fw-semibold mb-2" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
          <Zap size={16} /> Hardware Sensor Reading Simulation
        </span>
        <h1 className="display-6 fw-extrabold text-slate-900 mb-2">Optical Sensor Jaundice Screening</h1>
        <p className="text-muted">
          Input simulated optical sensor transmittance readings ($$0 - 255$$) or trigger preset hardware signals.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger py-2 px-3 small max-w-2xl mx-auto rounded-3 mb-4 d-flex align-items-center gap-2">
          <AlertCircle size={18} /> {error}
        </div>
      )}

      {!result ? (
        <div className="row justify-content-center">
          <div className="col-lg-8">
            <div className="medical-card p-4 p-md-5 border-0 shadow-lg">
              <form onSubmit={handleSubmit}>
                {/* Sensor Value Input Section */}
                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <label className="form-label fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                      <Sliders size={20} className="text-teal-600" /> Optical Sensor Value Input (0 - 255)
                    </label>
                    <span className="fs-4 fw-extrabold text-teal-700">{sensorValue}</span>
                  </div>

                  <input
                    type="range"
                    className="form-range mb-3"
                    min="0"
                    max="255"
                    value={sensorValue}
                    onChange={(e) => setSensorValue(e.target.value)}
                  />

                  <div className="input-group">
                    <span className="input-group-text bg-light fw-bold text-muted">Reading</span>
                    <input
                      type="number"
                      className="form-control form-control-lg bg-light fw-bold text-dark"
                      min="0"
                      max="255"
                      value={sensorValue}
                      onChange={(e) => setSensorValue(e.target.value)}
                      required
                    />
                  </div>

                  {/* Preset Simulation Buttons */}
                  <div className="mt-3">
                    <div className="extra-small text-muted mb-2 fw-semibold">Quick Simulation Presets:</div>
                    <div className="d-flex flex-wrap gap-2">
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-success extra-small"
                        onClick={() => setPreset(185)}
                      >
                        Sample Normal (185)
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-warning extra-small"
                        onClick={() => setPreset(85)}
                      >
                        Sample Mild Risk (85)
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-danger extra-small"
                        onClick={() => setPreset(42)}
                      >
                        Sample High Risk (42)
                      </button>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline-secondary extra-small d-flex align-items-center gap-1"
                        onClick={simulateRandomHardwareScan}
                      >
                        <RefreshCw size={12} /> Random Sensor Scan
                      </button>
                    </div>
                  </div>
                </div>

                {/* Live Gauge Preview */}
                <div className="mb-4">
                  <RiskGauge value={sensorValue} />
                </div>

                <hr className="my-4" />

                {/* Optional Patient Details */}
                <h6 className="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                  <User size={18} className="text-teal-600" /> Optional Patient Information
                </h6>

                <div className="row g-3 mb-4">
                  <div className="col-md-6">
                    <label className="form-label extra-small text-muted fw-semibold">Patient Name</label>
                    <input
                      type="text"
                      className="form-control bg-light py-2"
                      placeholder="Patient Name (Optional)"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>

                  <div className="col-md-3">
                    <label className="form-label extra-small text-muted fw-semibold">Age (Years)</label>
                    <input
                      type="number"
                      className="form-control bg-light py-2"
                      placeholder="Age"
                      min="0"
                      max="120"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                    />
                  </div>

                  <div className="col-md-3">
                    <label className="form-label extra-small text-muted fw-semibold">Gender</label>
                    <select
                      className="form-select bg-light py-2"
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Child">Child</option>
                      <option value="Unspecified">Unspecified</option>
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-medical w-100 py-3 btn-lg d-flex align-items-center justify-content-center gap-2 shadow"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="spinner-border spinner-border-sm" role="status"></span>
                  ) : (
                    <>
                      <PlayCircle size={22} /> Calculate Jaundice Risk & Save Record
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      ) : (
        <div className="row justify-content-center">
          <div className="col-lg-9">
            <ResultCard result={result} onReset={handleReset} />
          </div>
        </div>
      )}
    </div>
  );
};

export default Screening;
