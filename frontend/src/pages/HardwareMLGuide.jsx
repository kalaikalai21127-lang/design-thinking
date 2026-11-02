import React from 'react';
import { Cpu, Database, Zap, BookOpen, Layers, CheckCircle2, ArrowRight, AlertTriangle, ShieldCheck } from 'lucide-react';

const HardwareMLGuide = () => {
  return (
    <div className="container py-5">
      <div className="text-center max-w-3xl mx-auto mb-5">
        <span className="badge bg-teal-100 text-teal-800 py-2 px-3 rounded-pill fw-semibold mb-2" style={{ backgroundColor: '#ccfbf1', color: '#0f766e' }}>
          Design Thinking Technical Architecture
        </span>
        <h1 className="display-5 fw-extrabold text-slate-900 mb-2">NodeMCU ESP8266 & GY-9960 Hardware Guide</h1>
        <p className="lead text-muted">
          Technical specifications for connecting the GY-9960 (APDS-9960) colour sensor and SSD1306 OLED to the NodeMCU ESP8266, Port 80 Web Dashboard, and clinical calibration requirements.
        </p>
      </div>

      <div className="row g-4 mb-5">
        {/* Hardware Integration Section */}
        <div className="col-md-6">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <h4 className="fw-bold text-teal-700 mb-3 d-flex align-items-center gap-2" style={{ color: '#0d9488' }}>
              <Cpu size={24} /> 1. NodeMCU ESP8266 Hardware Setup
            </h4>
            <p className="text-muted small">
              The node uses the GY-9960 / APDS-9960 colour sensor and 0.96" SSD1306 OLED connected over the NodeMCU I²C bus.
            </p>

            <div className="p-3 bg-light rounded-3 border mb-3">
              <h6 className="fw-bold text-dark mb-2 extra-small text-uppercase">NodeMCU Pin Connections</h6>
              <table className="table table-sm table-bordered extra-small mb-0">
                <thead className="table-light">
                  <tr><th>Peripheral Pin</th><th>NodeMCU Pin</th><th>GPIO</th><th>Notes</th></tr>
                </thead>
                <tbody>
                  <tr><td><strong>GY-9960 SDA & OLED SDA</strong></td><td><strong>D2</strong></td><td>GPIO 4</td><td>Shared I²C Data (0x39 & 0x3C)</td></tr>
                  <tr><td><strong>GY-9960 SCL & OLED SCL</strong></td><td><strong>D1</strong></td><td>GPIO 5</td><td>Shared I²C Clock (100 kHz)</td></tr>
                  <tr><td><strong>Push Button</strong></td><td><strong>D6</strong></td><td>GPIO 12</td><td>Trigger Scan (INPUT_PULLUP to GND)</td></tr>
                  <tr><td><strong>Diagnostic LED</strong></td><td><strong>D5</strong></td><td>GPIO 14</td><td>Active HIGH (via 220–330Ω resistor)</td></tr>
                  <tr><td><strong>VCC</strong></td><td><strong>3.3V (3V3)</strong></td><td>3.3V</td><td>Power rail (Do NOT use 5V)</td></tr>
                  <tr><td><strong>GND</strong></td><td><strong>GND</strong></td><td>GND</td><td>Common system ground</td></tr>
                </tbody>
              </table>
            </div>

            <div className="alert alert-info py-2 px-3 extra-small border-0 rounded-3 mb-0">
              <strong>Firmware File:</strong> Located at <code>hardware/esp8266_sensor_node/esp8266_sensor_node.ino</code>. Hosts embedded Port 80 Web Dashboard directly on the NodeMCU.
            </div>
          </div>
        </div>

        {/* Photometrics & Calibration Section */}
        <div className="col-md-6">
          <div className="medical-card p-4 h-100 border-0 shadow-sm">
            <h4 className="fw-bold text-teal-700 mb-3 d-flex align-items-center gap-2" style={{ color: '#0d9488' }}>
              <Database size={24} /> 2. Bilirubin Optics & Calibration
            </h4>
            <p className="text-muted small">
              Bilirubin molecules attenuate blue-violet light with a peak optical extinction coefficient around <strong>450 - 460 nm</strong>.
            </p>

            <div className="p-3 bg-light rounded-3 border mb-3">
              <h6 className="fw-bold text-dark mb-2 extra-small text-uppercase">Six Spectral Bands Measured</h6>
              <ul className="text-muted extra-small ps-3 mb-0">
                <li className="mb-1"><strong>Violet (450 nm):</strong> Primary bilirubin absorption band.</li>
                <li className="mb-1"><strong>Blue (500 nm):</strong> Bilirubin absorption slope.</li>
                <li className="mb-1"><strong>Green (550 nm):</strong> Melanin / Hemoglobin baseline reference.</li>
                <li className="mb-1"><strong>Yellow (570 nm):</strong> Cutaneous tissue background.</li>
                <li className="mb-1"><strong>Orange (600 nm):</strong> Cutaneous tissue background.</li>
                <li className="mb-1"><strong>Red (650 nm):</strong> Deep tissue baseline reflectance.</li>
              </ul>
            </div>

            <div className="alert alert-warning py-2 px-3 extra-small border-0 rounded-3 mb-0">
              <strong>Clinical Calibration Requirement:</strong> Uncalibrated spectral readings default to <strong>Calibration Required</strong>. Pairing spectral ratios with clinical laboratory Serum Total Bilirubin (STB) blood tests is necessary before diagnostic risk classification.
            </div>
          </div>
        </div>
      </div>

      {/* Complete Hardware-to-Cloud Data Flow */}
      <div className="medical-card p-4 border-0 shadow-sm mb-5">
        <h5 className="fw-bold text-dark mb-4 text-center">Spectral Data Flow Architecture</h5>
        <div className="row text-center g-3 align-items-center">
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">Onboard White LED</div>
              <div className="extra-small text-muted">Light Source</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">Cutaneous Tissue</div>
              <div className="extra-small text-muted">Bilirubin Absorption (450nm)</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">AS7262 Sensor</div>
              <div className="extra-small text-muted">6 Calibrated Channels</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-light rounded-3 border">
              <div className="fw-bold text-dark small">ESP32 (GPIO 21/22)</div>
              <div className="extra-small text-muted">HTTP POST JSON</div>
            </div>
          </div>
          <div className="col-auto"><ArrowRight className="text-muted" size={16} /></div>
          <div className="col-md">
            <div className="p-3 bg-teal-50 border border-teal-200 rounded-3" style={{ backgroundColor: '#f0fdf4' }}>
              <div className="fw-bold text-teal-700 small">Flask API & DB</div>
              <div className="extra-small text-muted">Calibration Status & Dataset</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HardwareMLGuide;
