import React from 'react';
import { Activity, Cpu, ShieldAlert } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="mt-auto bg-white border-top py-4">
      <div className="container">
        <div className="row gy-4 align-items-center">
          <div className="col-md-5">
            <div className="d-flex align-items-center gap-2 fw-bold text-teal-700 fs-5 mb-2">
              <Activity className="text-teal-600" style={{ color: '#0d9488' }} size={22} />
              <span>Smart Jaundice Screening System</span>
            </div>
            <p className="text-muted small mb-0">
              Design Thinking Project — Low-cost non-invasive optical sensor screening platform with automated AI dataset collection.
            </p>
          </div>

          <div className="col-md-4">
            <div className="alert alert-info py-2 px-3 mb-0 small d-flex align-items-start gap-2 border-0 rounded-3" style={{ backgroundColor: '#e0f2fe', color: '#0369a1' }}>
              <ShieldAlert size={18} className="flex-shrink-0 mt-1" />
              <div>
                <strong>Optical Sensor System:</strong> Designed to simulate and process optical sensor hardware readings for early jaundice screening.
              </div>
            </div>
          </div>

          <div className="col-md-3 text-md-end text-muted small">
            <div className="d-flex align-items-center justify-content-md-end gap-1 mb-1">
              <Cpu size={14} className="text-teal-600" /> Future Hardware: ESP32 + TCS34725
            </div>
            <div>&copy; {new Date().getFullYear()} Design Thinking Team.</div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
