import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, Cpu, LayoutDashboard, History, Download, Home, PlayCircle } from 'lucide-react';
import { screeningAPI } from '../services/api';

const Navbar = () => {
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active text-teal-700 fw-bold' : '';

  return (
    <nav className="navbar navbar-expand-lg sticky-top navbar-medical shadow-sm py-3">
      <div className="container">
        {/* Brand Logo */}
        <Link className="navbar-brand d-flex align-items-center gap-2 fw-bold fs-4 text-teal-700" to="/">
          <div className="bg-teal-600 text-white p-2 rounded-3 d-flex align-items-center justify-content-center" style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #0d9488, #0284c7)' }}>
            <Activity size={24} />
          </div>
          <span>Opti<span style={{ color: '#0d9488' }}>Jaundice</span> MVP</span>
        </Link>

        {/* Mobile Toggle */}
        <button
          className="navbar-toggler border-0 shadow-none"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#optiNavbar"
          aria-controls="optiNavbar"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>

        {/* Links */}
        <div className="collapse navbar-collapse" id="optiNavbar">
          <ul className="navbar-nav me-auto mb-2 mb-lg-0 ms-lg-4 gap-1">
            <li className="nav-item">
              <Link className={`nav-link nav-link-custom d-flex align-items-center gap-1 ${isActive('/')}`} to="/">
                <Home size={18} /> Home
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link nav-link-custom d-flex align-items-center gap-1 ${isActive('/screening')}`} to="/screening">
                <PlayCircle size={18} /> Sensor Screening
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link nav-link-custom d-flex align-items-center gap-1 ${isActive('/dashboard')}`} to="/dashboard">
                <LayoutDashboard size={18} /> Dashboard
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link nav-link-custom d-flex align-items-center gap-1 ${isActive('/history')}`} to="/history">
                <History size={18} /> History & Dataset
              </Link>
            </li>
            <li className="nav-item">
              <Link className={`nav-link nav-link-custom d-flex align-items-center gap-1 ${isActive('/hardware-guide')}`} to="/hardware-guide">
                <Cpu size={18} /> Hardware & AI Guide
              </Link>
            </li>
          </ul>

          <div className="d-flex align-items-center gap-2">
            <a
              href={screeningAPI.getExportUrl()}
              className="btn btn-outline-medical d-flex align-items-center gap-2 py-2 px-3 small"
              target="_blank"
              rel="noopener noreferrer"
              title="Export Dataset for Machine Learning"
            >
              <Download size={16} /> Export AI Dataset (CSV)
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
