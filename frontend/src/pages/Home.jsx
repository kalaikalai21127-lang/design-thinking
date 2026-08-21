import React from 'react';
import { Link } from 'react-router-dom';
import { Activity, Cpu, ArrowRight, PlayCircle, ShieldCheck, Database, Zap, Layers } from 'lucide-react';

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
                <Zap size={16} /> Design Thinking Optical Screening System
              </span>
              <h1 className="display-4 fw-extrabold text-slate-900 mb-3" style={{ letterSpacing: '-0.02em' }}>
                Smart Jaundice Screening System Using <span style={{ color: '#0d9488' }}>Optical Sensor Readings</span>
              </h1>
              <p className="lead text-muted mb-4 pe-lg-4" style={{ fontSize: '1.2rem' }}>
                A low-cost, non-invasive optical screening framework that detects bilirubin accumulation using light absorption principles. Designed for future hardware deployment with ESP32 microcontrollers and machine learning model training.
              </p>
              <div className="d-flex flex-wrap gap-3">
                <Link to="/screening" className="btn btn-medical btn-lg d-flex align-items-center gap-2 px-4 shadow">
                  <PlayCircle size={22} /> Start Screening <ArrowRight size={20} />
                </Link>
                <Link to="/dashboard" className="btn btn-outline-medical btn-lg d-flex align-items-center gap-2 px-4">
                  View Dashboard Analytics
                </Link>
              </div>
            </div>

            <div className="col-lg-5 text-center">
              <div className="medical-card p-4 mx-auto text-center position-relative shadow-lg" style={{ maxWidth: '420px' }}>
                <div className="p-4 bg-teal-50 rounded-3 border mb-3" style={{ backgroundColor: '#f0fdf4' }}>
                  <div className="d-flex justify-content-center mb-3">
                    <div className="p-3 bg-white rounded-circle shadow-sm">
                      <Activity size={56} style={{ color: '#0d9488' }} />
                    </div>
                  </div>
                  <h5 className="fw-bold text-dark mb-1">Optical Transmittance Spectrum</h5>
                  <p className="extra-small text-muted mb-0">Simulated Hardware Range (0 - 255)</p>
                </div>

                <div className="row g-2 text-start small">
                  <div className="col-4">
                    <div className="p-2 bg-success bg-opacity-10 border border-success rounded text-success text-center">
                      <div className="fw-bold">100 - 255</div>
                      <div className="extra-small">Normal</div>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 bg-warning bg-opacity-10 border border-warning rounded text-warning text-center">
                      <div className="fw-bold">70 - 99</div>
                      <div className="extra-small">Mild Risk</div>
                    </div>
                  </div>
                  <div className="col-4">
                    <div className="p-2 bg-danger bg-opacity-10 border border-danger rounded text-danger text-center">
                      <div className="fw-bold">0 - 69</div>
                      <div className="extra-small">High Risk</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How System Works */}
      <section className="py-5 bg-white">
        <div className="container py-4">
          <div className="text-center max-w-2xl mx-auto mb-5">
            <h2 className="fw-extrabold text-slate-900 mb-2">How the Optical Screening System Works</h2>
            <p className="text-muted">Multi-stage architecture bridging physical optical sensors, rule-based MVP, and future AI training.</p>
          </div>

          <div className="row g-4">
            <div className="col-md-3">
              <div className="medical-card p-4 h-100 border-0 shadow-sm text-center">
                <div className="p-3 rounded-circle bg-teal-100 text-teal-800 d-inline-flex mb-3" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
                  <Zap size={28} />
                </div>
                <h5 className="fw-bold mb-2">1. LED Light Source</h5>
                <p className="text-muted extra-small mb-0">
                  Calibrated LED emits light through tissue/finger. Bilirubin absorbs specific wavelengths (450-460nm).
                </p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 border-0 shadow-sm text-center">
                <div className="p-3 rounded-circle bg-cyan-100 text-cyan-800 d-inline-flex mb-3" style={{ backgroundColor: '#e0f2fe', color: '#0369a1' }}>
                  <Activity size={28} />
                </div>
                <h5 className="fw-bold mb-2">2. Optical Sensor</h5>
                <p className="text-muted extra-small mb-0">
                  Color sensor (TCS34725/LDR) measures transmitted light intensity and converts to digital reading (0-255).
                </p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 border-0 shadow-sm text-center">
                <div className="p-3 rounded-circle bg-amber-100 text-amber-800 d-inline-flex mb-3" style={{ backgroundColor: '#fef3c7', color: '#92400e' }}>
                  <Layers size={28} />
                </div>
                <h5 className="fw-bold mb-2">3. Flask REST API</h5>
                <p className="text-muted extra-small mb-0">
                  Backend applies configurable thresholds to classify risk (Normal, Mild, High) and logs data to database.
                </p>
              </div>
            </div>

            <div className="col-md-3">
              <div className="medical-card p-4 h-100 border-0 shadow-sm text-center">
                <div className="p-3 rounded-circle bg-emerald-100 text-emerald-800 d-inline-flex mb-3" style={{ backgroundColor: '#d1fae5', color: '#065f46' }}>
                  <Database size={28} />
                </div>
                <h5 className="fw-bold mb-2">4. AI Dataset Collection</h5>
                <p className="text-muted extra-small mb-0">
                  All readings form a structured CSV dataset for future machine learning classifier model training.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
