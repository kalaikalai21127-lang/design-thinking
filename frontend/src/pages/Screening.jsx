import React, { useState } from 'react';
import { screeningAPI } from '../services/api';
import ResultCard from '../components/ResultCard';
import { PlayCircle, Sliders, User, AlertCircle, RefreshCw, Zap, Cpu, Sparkles } from 'lucide-react';

const Screening = () => {
  // AS7262 Six Spectral Channel State (calibrated irradiance uW/cm^2)
  const [channels, setChannels] = useState({
    violet: 12.45,  // 450 nm - Bilirubin peak absorption band
    blue: 18.30,    // 500 nm - Secondary absorption
    green: 28.40,   // 550 nm - Reference hemoglobin band
    yellow: 24.15,  // 570 nm - Tissue reference
    orange: 19.80,  // 600 nm - Tissue reference
    red: 14.20      // 650 nm - Cutaneous baseline reflectance
  });

  const [name, setName] = useState('');
  const [age, setAge] = useState('');
  const [gender, setGender] = useState('Male');

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChannelChange = (channelName, value) => {
    const val = parseFloat(value);
    setChannels(prev => ({
      ...prev,
      [channelName]: isNaN(val) ? 0 : val
    }));
  };

  const setPreset = (v, b, g, y, o, r) => {
    setChannels({
      violet: v,
      blue: b,
      green: g,
      yellow: y,
      orange: o,
      red: r
    });
    setResult(null);
  };

  const simulateRandomScan = () => {
    setChannels({
      violet: parseFloat((Math.random() * 25 + 5).toFixed(2)),
      blue: parseFloat((Math.random() * 25 + 10).toFixed(2)),
      green: parseFloat((Math.random() * 25 + 15).toFixed(2)),
      yellow: parseFloat((Math.random() * 25 + 15).toFixed(2)),
      orange: parseFloat((Math.random() * 20 + 10).toFixed(2)),
      red: parseFloat((Math.random() * 15 + 8).toFixed(2))
    });
    setResult(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await screeningAPI.predict({
        sensor_type: 'AS7262',
        channels: channels,
        violet: channels.violet,
        blue: channels.blue,
        green: channels.green,
        yellow: channels.yellow,
        orange: channels.orange,
        red: channels.red,
        name: name.trim() || 'Neonatal Test Alpha',
        age: parseInt(age, 10) || 0,
        gender: gender,
        sensor_value: 0
      });
      setResult(data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to process AS7262 spectral screening.');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError('');
  };

  return (
    <div className="container py-5">
      <div className="text-center max-w-2xl mx-auto mb-5">
        <span className="badge bg-teal-100 text-teal-800 py-2 px-3 rounded-pill fw-semibold mb-2" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
          <Cpu size={16} /> AS7262 Six-Channel Spectral Sensor Node
        </span>
        <h1 className="display-6 fw-extrabold text-slate-900 mb-2">Neonatal Jaundice Spectral Screening</h1>
        <p className="text-muted">
          Input AMS AS7262 calibrated optical spectral values across 6 visible bands (450 nm - 650 nm) or load experimental test profiles.
        </p>
      </div>

      {error && (
        <div className="alert alert-danger py-2 px-3 small max-w-2xl mx-auto rounded-3 mb-4 d-flex align-items-center gap-2">
          <AlertCircle size={18} /> {error}
        </div>
      )}

      {!result ? (
        <div className="row justify-content-center">
          <div className="col-lg-9">
            <div className="medical-card p-4 p-md-5 border-0 shadow-lg">
              <form onSubmit={handleSubmit}>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <h5 className="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                    <Sliders size={20} className="text-teal-600" /> Spectral Channels (&mu;W/cm&sup2;)
                  </h5>
                  <button type="button" className="btn btn-sm btn-outline-secondary" onClick={simulateRandomScan}>
                    <RefreshCw size={14} className="me-1" /> Random Scan
                  </button>
                </div>

                <div className="row g-3 mb-4">
                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#ede9fe', borderColor: '#ddd6fe' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#6d28d9' }}>
                        450 nm Violet (Bilirubin Peak)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.violet}
                        onChange={(e) => handleChannelChange('violet', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#dbeafe', borderColor: '#bfdbfe' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#1d4ed8' }}>
                        500 nm Blue (Slope)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.blue}
                        onChange={(e) => handleChannelChange('blue', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#dcfce7', borderColor: '#bbf7d0' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#15803d' }}>
                        550 nm Green (Reference Band)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.green}
                        onChange={(e) => handleChannelChange('green', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#fef9c3', borderColor: '#fef08a' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#a16207' }}>
                        570 nm Yellow (Tissue Ref)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.yellow}
                        onChange={(e) => handleChannelChange('yellow', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#ffedd5', borderColor: '#fed7aa' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#c2410c' }}>
                        600 nm Orange (Tissue Ref)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.orange}
                        onChange={(e) => handleChannelChange('orange', e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="col-md-4">
                    <div className="p-3 rounded-3 border" style={{ background: '#fee2e2', borderColor: '#fecaca' }}>
                      <label className="form-label small fw-bold mb-1" style={{ color: '#b91c1c' }}>
                        650 nm Red (Skin Baseline)
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        className="form-control form-control-lg fw-bold"
                        value={channels.red}
                        onChange={(e) => handleChannelChange('red', e.target.value)}
                        required
                      />
                    </div>
                  </div>
                </div>

                {/* Preset Profiles */}
                <div className="mb-4">
                  <div className="extra-small text-muted fw-semibold mb-2">Preset Test Profiles:</div>
                  <div className="d-flex flex-wrap gap-2">
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => setPreset(16.5, 22.1, 32.4, 28.1, 22.0, 16.2)}
                    >
                      Normal Neonatal Skin Baseline
                    </button>
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-warning"
                      onClick={() => setPreset(7.2, 14.5, 30.8, 29.5, 23.4, 17.1)}
                    >
                      Elevated Bilirubin Prototype (High 450nm Attenuation)
                    </button>
                    <button
                      type="button"
                      className="btn btn-sm btn-outline-secondary"
                      onClick={() => setPreset(45.0, 48.0, 50.0, 49.0, 48.0, 46.0)}
                    >
                      Calibrated White Reference Tile
                    </button>
                  </div>
                </div>

                <hr className="my-4" />

                {/* Subject Demographic Inputs */}
                <h6 className="fw-bold mb-3 d-flex align-items-center gap-2">
                  <User size={18} className="text-teal-600" /> Optional Subject Details
                </h6>
                <div className="row g-3 mb-4">
                  <div className="col-md-6">
                    <label className="form-label small text-muted">Subject / Patient Name or ID</label>
                    <input
                      type="text"
                      className="form-control bg-light py-2"
                      placeholder="e.g. Neonate Node 101"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                    />
                  </div>
                  <div className="col-md-3">
                    <label className="form-label small text-muted">Age (Days / Hours)</label>
                    <input
                      type="number"
                      className="form-control bg-light py-2"
                      placeholder="0"
                      min="0"
                      max="365"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                    />
                  </div>
                  <div className="col-md-3">
                    <label className="form-label small text-muted">Gender</label>
                    <select
                      className="form-select bg-light py-2"
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                    >
                      <option value="Male">Male</option>
                      <option value="Female">Female</option>
                      <option value="Unspecified">Unspecified</option>
                    </select>
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn btn-medical btn-lg w-100 py-3 d-flex align-items-center justify-content-center gap-2 shadow"
                >
                  {loading ? (
                    <span>Processing Spectral Data...</span>
                  ) : (
                    <>
                      <PlayCircle size={20} />
                      <span>Log Spectral Screening & Evaluate Calibration Status</span>
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
