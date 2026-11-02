import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Cpu, ArrowRight, PlayCircle, ShieldCheck, Database, Zap, Layers, AlertTriangle } from 'lucide-react';

const Home = () => {
  return (
    <div className="flex-grow-1">
      {/* Hero Header */}
      <section className="hero-bg py-5 border-bottom">
        <div className="hero-glow"></div>
        <div className="container py-lg-5">
          <div className="row align-items-center gy-5">
            <div className="col-lg-7">
              <span className="badge bg-teal-100 text-teal-800 py-2 px-3 rounded-pill fw-semibold mb-3 d-inline-flex align-items-center gap-2" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
                <Cpu size={16} /> ESP32 & AS7262 Spectral Screening Node
              </span>
              <h1 className="display-4 fw-extrabold text-slate-900 mb-3" style={{ letterSpacing: '-0.02em' }}>
                Low-Cost Neonatal Jaundice Screening Using <span style={{ color: '#0d9488' }}>AS7262 Spectral Sensor</span>
              </h1>
              <p className="lead text-muted mb-4 pe-lg-4" style={{ fontSize: '1.2rem' }}>
                A multi-spectral optical prototype measuring 6 discrete visible wavelengths (450nm - 650nm) to assess neonatal bilirubin attenuation. Engineered with ESP32 microcontroller firmware and an open REST backend.
              </p>

              <div className="alert alert-warning py-3 px-3 rounded-3 border-0 mb-4 small d-flex align-items-start gap-2">
                <AlertTriangle size={20} className="text-warning flex-shrink-0 mt-1" />
                <div>
                  <strong>Research Prototype Notice:</strong> This device is an experimental prototype, not a clinically approved diagnostic medical device. Uncalibrated spectral readings must not be used to diagnose jaundice without clinical laboratory calibration against Serum Total Bilirubin (STB).
                </div>
              </div>

              <div className="d-flex flex-wrap gap-3">
                <Link to="/screening" className="btn btn-medical btn-lg d-flex align-items-center gap-2 px-4 shadow">
                  <PlayCircle size={22} /> Start Spectral Screening <ArrowRight size={20} />
                </Link>
                <Link to="/hardware-guide" className="btn btn-outline-medical btn-lg d-flex align-items-center gap-2 px-4">
                  ESP32 & AS7262 Guide
                </Link>
              </div>
            </div>

            <div className="col-lg-5 text-center">
              <div className="medical-card p-4 mx-auto text-center position-relative shadow-lg" style={{ maxWidth: '440px' }}>
                <div className="p-4 bg-teal-50 rounded-3 border mb-3" style={{ backgroundColor: '#f0fdf4' }}>
                  <div className="d-flex justify-content-center mb-3">
                    <div className="p-3 bg-white rounded-circle shadow-sm">
                      <Activity size={48} style={{ color: '#0d9488' }} />
                    </div>
                  </div>
                  <h5 className="fw-bold text-dark mb-1">AS7262 Visible Spectrum</h5>
                  <p className="extra-small text-muted mb-0">6 Calibrated Optical Bands (450nm - 650nm)</p>
                </div>

                <div className="row g-2 text-start small">
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#ede9fe', borderColor: '#ddd6fe' }}>
                      <strong className="d-block" style={{ color: '#6d28d9' }}>450nm Violet</strong>
                      <span className="extra-small text-muted">Bilirubin absorption</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#dbeafe', borderColor: '#bfdbfe' }}>
                      <strong className="d-block" style={{ color: '#1d4ed8' }}>500nm Blue</strong>
                      <span className="extra-small text-muted">Absorption slope</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#dcfce7', borderColor: '#bbf7d0' }}>
                      <strong className="d-block" style={{ color: '#15803d' }}>550nm Green</strong>
                      <span className="extra-small text-muted">Hb reference band</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#fef9c3', borderColor: '#fef08a' }}>
                      <strong className="d-block" style={{ color: '#a16207' }}>570nm Yellow</strong>
                      <span className="extra-small text-muted">Tissue reference</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#ffedd5', borderColor: '#fed7aa' }}>
                      <strong className="d-block" style={{ color: '#c2410c' }}>600nm Orange</strong>
                      <span className="extra-small text-muted">Tissue reference</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="p-2 border rounded text-center" style={{ background: '#fee2e2', borderColor: '#fecaca' }}>
                      <strong className="d-block" style={{ color: '#b91c1c' }}>650nm Red</strong>
                      <span className="extra-small text-muted">Skin baseline</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4 Pillars Section */}
      <section className="py-5 bg-white">
        <div className="container">
          <div className="text-center max-w-2xl mx-auto mb-5">
            <h2 className="fw-extrabold text-slate-900 mb-2">How Spectral Bilirubin Screening Works</h2>
            <p className="text-muted">4-Step Data Pipeline connecting the AS7262 Sensor to Cloud AI</p>
          </div>

          <div className="row g-4">
            <div className="col-md-3">
              <div className="medical-card p-4 h-100 text-center">
                <div className="p-3 rounded-circle bg-teal-50 text-teal-700 d-inline-flex mb-3" style={{ color: '#0d9488' }}>
                  <Zap size={24} />
                </div>
                <h5 className="fw-bold mb-2">1. LED Illumination</h5>
                <p className="text-muted small mb-0">AS7262 onboard white LED illuminates cutaneous tissue safely.</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 text-center">
                <div className="p-3 rounded-circle bg-emerald-50 text-emerald-700 d-inline-flex mb-3" style={{ color: '#059669' }}>
                  <Cpu size={24} />
                </div>
                <h5 className="fw-bold mb-2">2. AS7262 Sensor</h5>
                <p className="text-muted small mb-0">Optical interference filters capture 6 calibrated visible bands (450nm-650nm).</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 text-center">
                <div className="p-3 rounded-circle bg-amber-50 text-amber-700 d-inline-flex mb-3" style={{ color: '#d97706' }}>
                  <Database size={24} />
                </div>
                <h5 className="fw-bold mb-2">3. ESP32 Wi-Fi Node</h5>
                <p className="text-muted small mb-0">Microcontroller reads I²C registers (SDA=21, SCL=22) and posts JSON to backend.</p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 text-center">
                <div className="p-3 rounded-circle bg-indigo-50 text-indigo-700 d-inline-flex mb-3" style={{ color: '#4f46e5' }}>
                  <Layers size={24} />
                </div>
                <h5 className="fw-bold mb-2">4. Dataset & Calibration</h5>
                <p className="text-muted small mb-0">Builds spectral dataset for future clinical calibration against blood STB.</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
