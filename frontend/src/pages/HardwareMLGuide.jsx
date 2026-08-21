import React from 'react';
import { Cpu, Database, Zap, BookOpen, Layers, CheckCircle2, ArrowRight } from 'lucide-react';

const HardwareMLGuide = () => {
  return (
    <div className="container py-5">
      <div className="text-center max-w-3xl mx-auto mb-5">
        <span className="badge bg-teal-100 text-teal-800 py-2 px-3 rounded-pill fw-semibold mb-2" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
          Design Thinking Technical Architecture
        </span>
        <h1 className="display-5 fw-extrabold text-slate-900 mb-2">Hardware Integration & AI Roadmap</h1>
        <p className="lead text-muted">
          Detailed blueprint for connecting ESP32 physical optical sensors and replacing MVP rule-based logic with Machine Learning classifiers.
        </p>
      </div>

      <div className="row g-4 mb-5">
        {/* Hardware Integration Section */}
        <div className="col-md-6">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <h4 className="fw-bold text-teal-700 mb-3 d-flex align-items-center gap-2" style={{ color: '#0d9488' }}>
              <Cpu size={24} /> 1. Future ESP32 Hardware Integration
            </h4>
            <p className="text-muted small">
              The MVP web interface is architected to seamlessly receive optical sensor data directly from physical microcontrollers without changing the frontend UI.
            </p>

            <div className="p-3 bg-light rounded-3 border mb-3">
              <h6 className="fw-bold text-dark mb-2 extra-small text-uppercase">Component Stack</h6>
              <ul className="text-muted extra-small ps-3 mb-0">
                <li className="mb-1"><strong>Microcontroller:</strong> ESP32 Wi-Fi / NodeMCU</li>
                <li className="mb-1"><strong>Optical Sensor:</strong> TCS34725 / TCS3200 Color Sensor</li>
                <li className="mb-1"><strong>Light Emitter:</strong> 460nm Blue / High-Intensity White LED</li>
                <li className="mb-1"><strong>Detector:</strong> LDR / Photodiode Transmittance Cell</li>
              </ul>
            </div>

            <div className="alert alert-info py-2 px-3 extra-small border-0 rounded-3">
              <strong>C++ Firmware File:</strong> Located at <code>hardware/esp32_sensor_node.ino</code>. Sends HTTP POST requests directly to <code>POST /api/predict</code>.
            </div>
          </div>
        </div>

        {/* AI Dataset & ML Section */}
        <div className="col-md-6">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <h4 className="fw-bold text-teal-700 mb-3 d-flex align-items-center gap-2" style={{ color: '#0d9488' }}>
              <Database size={24} /> 2. Machine Learning Model Transition
            </h4>
            <p className="text-muted small">
              Every sensor reading captured in the SQLite database automatically forms part of an AI dataset for future supervised ML classifier training.
            </p>

            <div className="p-3 bg-light rounded-3 border mb-3">
              <h6 className="fw-bold text-dark mb-2 extra-small text-uppercase">4-Step AI Workflow</h6>
              <ol className="text-muted extra-small ps-3 mb-0">
                <li className="mb-1"><strong>Collect Data:</strong> Store optical sensor readings ($$0 - 255$$) in SQLite.</li>
                <li className="mb-1"><strong>Export CSV:</strong> Download dataset via <code>GET /export-dataset</code>.</li>
                <li className="mb-1"><strong>Train Model:</strong> Execute <code>python ml/train_model.py</code> to train Random Forest.</li>
                <li className="mb-1"><strong>Deploy AI:</strong> Activate <code>ml/predict.py</code> to override rule-based thresholds.</li>
              </ol>
            </div>

            <div className="alert alert-success py-2 px-3 extra-small border-0 rounded-3">
              <strong>ML Placeholder Files:</strong> Prepared in <code>ml/train_model.py</code> and <code>ml/predict.py</code>.
            </div>
          </div>
        </div>
      </div>

      {/* Complete Hardware-to-Cloud Data Flow */}
      <div className="medical-card p-4 border-0 shadow-sm mb-5">
        <h5 className="fw-bold text-dark mb-4 text-center">Hardware-to-Cloud Data Flow Architecture</h5>
        <div className="row text-center g-3 align-items-center">
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">Diagnostic LED</div>
              <div className="extra-small text-muted">Light Source</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">Tissue / Finger</div>
              <div className="extra-small text-muted">Transmittance</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">Optical Sensor</div>
              <div className="extra-small text-muted">TCS34725 ADC</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">ESP32 Wi-Fi</div>
              <div className="extra-small text-muted">HTTP POST</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-teal-50 border border-teal-200 rounded-3" style={{ backgroundColor: '#f0fdf4' }}>
              <div className="fw-bold text-teal-700 small">Flask API & DB</div>
              <div className="extra-small text-muted">Prediction Engine</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HardwareMLGuide;
