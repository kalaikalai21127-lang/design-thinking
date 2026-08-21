import os
import sys
import csv
import io
from datetime import datetime

# Ensure backend directory is in sys.path before local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS

from config import Config
from models import db, Patient, Screening

# Full Standalone Medical UI HTML Template with standard HTML 'class' attributes & modern medical CSS
UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Jaundice Screening System Using Optical Sensor Readings</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <style>
        :root {
            --primary-teal: #0d9488;
            --primary-teal-dark: #0f766e;
            --primary-teal-light: #ccfbf1;
            --accent-cyan: #0284c7;
            --dark-navy: #0f172a;
            --slate-muted: #64748b;
            --light-bg: #f8fafc;
        }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--light-bg);
            color: var(--dark-navy);
            margin: 0;
            padding: 0;
            min-height: 100vh;
        }

        .navbar-medical {
            background: rgba(255, 255, 255, 0.95) !important;
            backdrop-filter: blur(12px);
            border-bottom: 1px solid #e2e8f0;
        }

        .hero-bg {
            background: radial-gradient(circle at 10% 20%, rgba(13, 148, 136, 0.08) 0%, rgba(2, 132, 199, 0.05) 90%), #ffffff;
            position: relative;
            overflow: hidden;
        }

        .medical-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 16px;
            box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.06);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .medical-card:hover {
            box-shadow: 0 16px 35px -8px rgba(13, 148, 136, 0.15);
            transform: translateY(-2px);
        }

        .btn-medical {
            background: linear-gradient(135deg, var(--primary-teal) 0%, var(--accent-cyan) 100%);
            color: #ffffff !important;
            border: none;
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 24px;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3);
            transition: all 0.3s ease;
        }

        .btn-medical:hover {
            opacity: 0.95;
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(13, 148, 136, 0.45);
        }

        .btn-outline-medical {
            border: 2px solid var(--primary-teal);
            color: var(--primary-teal) !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 8px 22px;
            background: transparent;
            transition: all 0.3s ease;
        }

        .btn-outline-medical:hover {
            background: var(--primary-teal-light);
            color: var(--primary-teal-dark) !important;
        }

        .badge-normal {
            background-color: #d1fae5;
            color: #065f46;
            font-weight: 700;
        }

        .badge-mild {
            background-color: #fef3c7;
            color: #92400e;
            font-weight: 700;
        }

        .badge-high {
            background-color: #ffe4e6;
            color: #9f1239;
            font-weight: 700;
        }

        .text-teal {
            color: var(--primary-teal) !important;
        }

        .extra-small {
            font-size: 0.78rem;
        }
    </style>
</head>
<body class="d-flex flex-column min-vh-100">

    <!-- Header Navigation -->
    <nav class="navbar navbar-expand-lg sticky-top navbar-medical py-3 shadow-sm">
        <div class="container">
            <a class="navbar-brand d-flex align-items-center gap-2 fw-bold text-dark fs-4" href="#" onclick="showSection('home')">
                <div class="p-2 rounded-3 text-white d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; background: linear-gradient(135deg, #0d9488, #0284c7);">
                    <i class="bi bi-activity fs-5"></i>
                </div>
                <span>Opti<span class="text-teal">Jaundice</span> MVP</span>
            </a>
            <button class="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navMenu">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0 ms-lg-4 gap-1 fw-semibold">
                    <li class="nav-item"><a class="nav-link text-dark py-2 px-3 rounded-3" href="#" onclick="showSection('home')"><i class="bi bi-house me-1"></i> Home</a></li>
                    <li class="nav-item"><a class="nav-link text-dark py-2 px-3 rounded-3" href="#" onclick="showSection('screening')"><i class="bi bi-play-circle me-1"></i> Sensor Screening</a></li>
                    <li class="nav-item"><a class="nav-link text-dark py-2 px-3 rounded-3" href="#" onclick="showSection('dashboard')"><i class="bi bi-grid me-1"></i> Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link text-dark py-2 px-3 rounded-3" href="#" onclick="showSection('history')"><i class="bi bi-clock-history me-1"></i> History & Dataset</a></li>
                    <li class="nav-item"><a class="nav-link text-dark py-2 px-3 rounded-3" href="#" onclick="showSection('hardware')"><i class="bi bi-cpu me-1"></i> Hardware & AI Guide</a></li>
                </ul>
                <a href="/export-dataset" class="btn btn-outline-medical py-2 px-3 small d-flex align-items-center gap-2" target="_blank">
                    <i class="bi bi-download"></i> Export AI Dataset (CSV)
                </a>
            </div>
        </div>
    </nav>

    <!-- SECTION 1: HOME PAGE -->
    <div id="sec-home" class="section-block">
        <section class="hero-bg py-5 border-bottom">
            <div class="container py-lg-4">
                <div class="row align-items-center gy-5">
                    <div class="col-lg-7">
                        <span class="badge py-2 px-3 rounded-pill fw-semibold mb-3 d-inline-flex align-items-center gap-1" style="background-color: #ccfbf1; color: #0f766e;">
                            <i class="bi bi-lightning-charge"></i> Design Thinking Optical Screening System
                        </span>
                        <h1 className="display-4 fw-extrabold text-dark mb-3" style="letter-spacing: -0.02em;">
                            Smart Jaundice Screening System Using <span class="text-teal">Optical Sensor Readings</span>
                        </h1>
                        <p class="lead text-muted mb-4 pe-lg-4">
                            A low-cost, non-invasive optical screening platform that measures light transmittance through tissue to detect bilirubin yellowing. Built for future hardware integration with ESP32 microcontrollers and AI machine learning models.
                        </p>
                        <div class="d-flex flex-wrap gap-3">
                            <button class="btn btn-medical btn-lg d-flex align-items-center gap-2 shadow" onclick="showSection('screening')">
                                <i class="bi bi-play-circle-fill"></i> Start Sensor Screening
                            </button>
                            <button class="btn btn-outline-medical btn-lg" onclick="showSection('dashboard')">
                                View Dashboard Analytics
                            </button>
                        </div>
                    </div>
                    <div class="col-lg-5 text-center">
                        <div class="medical-card p-4 mx-auto shadow-lg" style="max-width: 400px;">
                            <div class="p-4 rounded-3 border mb-3 text-center" style="background-color: #f0fdf4;">
                                <i class="bi bi-activity text-teal display-3"></i>
                                <h5 class="fw-bold mt-2 mb-1">Optical Transmittance Spectrum</h5>
                                <p class="extra-small text-muted mb-0">Hardware Transmittance Range (0 - 255)</p>
                            </div>
                            <div class="row g-2 text-start small">
                                <div class="col-4">
                                    <div class="p-2 border border-success rounded text-center badge-normal">
                                        <strong class="text-success d-block">100 - 255</strong>
                                        <span class="extra-small">Normal</span>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="p-2 border border-warning rounded text-center badge-mild">
                                        <strong class="text-warning d-block">70 - 99</strong>
                                        <span class="extra-small">Mild Risk</span>
                                    </div>
                                </div>
                                <div class="col-4">
                                    <div class="p-2 border border-danger rounded text-center badge-high">
                                        <strong class="text-danger d-block">0 - 69</strong>
                                        <span class="extra-small">High Risk</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section class="py-5 bg-white">
            <div class="container">
                <div class="text-center max-w-2xl mx-auto mb-5">
                    <h2 class="fw-extrabold mb-2">How the System Works</h2>
                    <p class="text-muted">4-Step Data Pipeline connecting Optical Sensors to Cloud AI</p>
                </div>
                <div class="row g-4">
                    <div class="col-md-3">
                        <div class="medical-card p-4 h-100 text-center">
                            <div class="p-3 rounded-circle bg-light text-teal d-inline-flex mb-3"><i class="bi bi-lightbulb fs-3"></i></div>
                            <h5 class="fw-bold mb-2">1. LED Emitter</h5>
                            <p class="text-muted small">Calibrated light source penetrates tissue; bilirubin absorbs 450-460nm light.</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="medical-card p-4 h-100 text-center">
                            <div class="p-3 rounded-circle bg-light text-success d-inline-flex mb-3"><i class="bi bi-cpu fs-3"></i></div>
                            <h5 class="fw-bold mb-2">2. Optical Sensor</h5>
                            <p class="text-muted small">TCS34725 / Photodiode measures light intensity and outputs 0-255 ADC value.</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="medical-card p-4 h-100 text-center">
                            <div class="p-3 rounded-circle bg-light text-warning d-inline-flex mb-3"><i class="bi bi-hdd-stack fs-3"></i></div>
                            <h5 class="fw-bold mb-2">3. Flask REST API</h5>
                            <p class="text-muted small">Backend evaluates risk thresholds and stores records permanently in SQLite.</p>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="medical-card p-4 h-100 text-center">
                            <div class="p-3 rounded-circle bg-light text-info d-inline-flex mb-3"><i class="bi bi-robot fs-3"></i></div>
                            <h5 class="fw-bold mb-2">4. AI Training</h5>
                            <p class="text-muted small">Exported CSV datasets train future Random Forest machine learning models.</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </div>

    <!-- SECTION 2: SENSOR SCREENING -->
    <div id="sec-screening" class="section-block d-none py-5">
        <div class="container">
            <div class="text-center max-w-2xl mx-auto mb-4">
                <h2 class="fw-extrabold mb-2">Optical Sensor Jaundice Screening</h2>
                <p class="text-muted">Simulate optical transmittance readings (0 - 255) or trigger hardware presets.</p>
            </div>

            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="medical-card p-4 p-md-5">
                        <form id="screeningForm" onsubmit="handleScreeningSubmit(event)">
                            <div class="mb-4">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <label class="form-label fw-bold mb-0"><i class="bi bi-sliders me-2 text-teal"></i> Sensor Reading Input (0 - 255)</label>
                                    <span id="sliderValDisplay" class="fs-3 fw-extrabold text-teal">120</span>
                                </div>
                                <input type="range" class="form-range mb-3" id="sensorRange" min="0" max="255" value="120" oninput="updateRangeVal(this.value)">
                                <div class="input-group mb-3">
                                    <span class="input-group-text bg-light fw-bold">Reading Value</span>
                                    <input type="number" class="form-control form-control-lg fw-bold" id="sensorInput" min="0" max="255" value="120" oninput="updateRangeVal(this.value)" required>
                                </div>

                                <div class="mt-3">
                                    <div class="extra-small text-muted fw-semibold mb-2">Quick Simulation Presets:</div>
                                    <div class="d-flex flex-wrap gap-2">
                                        <button type="button" class="btn btn-sm btn-outline-success" onclick="setPresetVal(185)">Sample Normal (185)</button>
                                        <button type="button" class="btn btn-sm btn-outline-warning" onclick="setPresetVal(85)">Sample Mild Risk (85)</button>
                                        <button type="button" class="btn btn-sm btn-outline-danger" onclick="setPresetVal(42)">Sample High Risk (42)</button>
                                        <button type="button" class="btn btn-sm btn-outline-secondary" onclick="randomScan()"><i class="bi bi-shuffle me-1"></i> Random Scan</button>
                                    </div>
                                </div>
                            </div>

                            <hr class="my-4">

                            <h6 class="fw-bold mb-3"><i class="bi bi-person me-2 text-teal"></i> Optional Patient Details</h6>
                            <div class="row g-3 mb-4">
                                <div class="col-md-6">
                                    <label class="form-label small text-muted">Patient Name</label>
                                    <input type="text" class="form-control bg-light py-2" id="patientName" placeholder="Patient Name (Optional)">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label small text-muted">Age (Years)</label>
                                    <input type="number" class="form-control bg-light py-2" id="patientAge" placeholder="Age" min="0" max="120">
                                </div>
                                <div class="col-md-3">
                                    <label class="form-label small text-muted">Gender</label>
                                    <select class="form-select bg-light py-2" id="patientGender">
                                        <option value="Male">Male</option>
                                        <option value="Female">Female</option>
                                        <option value="Child">Child</option>
                                        <option value="Unspecified">Unspecified</option>
                                    </select>
                                </div>
                            </div>

                            <button type="submit" class="btn btn-medical btn-lg w-100 py-3 d-flex align-items-center justify-content-center gap-2 shadow">
                                <i class="bi bi-play-circle-fill fs-5"></i> Calculate Jaundice Risk & Save Record
                            </button>
                        </form>

                        <div id="resultCardBox" class="mt-4 d-none">
                            <!-- Dynamic Result Output Card -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SECTION 3: DASHBOARD -->
    <div id="sec-dashboard" class="section-block d-none py-5">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-extrabold mb-1">Optical Jaundice Analytics Dashboard</h2>
                    <p class="text-muted mb-0">System metrics and risk distribution statistics</p>
                </div>
                <button class="btn btn-outline-medical btn-sm" onclick="loadDashboardData()"><i class="bi bi-arrow-clockwise me-1"></i> Refresh Stats</button>
            </div>

            <div class="row g-3 mb-4">
                <div class="col-md-3">
                    <div class="medical-card p-4 border-0 shadow-sm">
                        <div class="text-muted extra-small text-uppercase fw-bold mb-1">Total Screenings</div>
                        <h2 id="dashTotal" class="fw-extrabold text-dark mb-0">0</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="medical-card p-4 border-0 shadow-sm">
                        <div class="text-muted extra-small text-uppercase fw-bold mb-1">Normal Cases</div>
                        <h2 id="dashNormal" class="fw-extrabold text-success mb-0">0</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="medical-card p-4 border-0 shadow-sm">
                        <div class="text-muted extra-small text-uppercase fw-bold mb-1">Mild Risk Cases</div>
                        <h2 id="dashMild" class="fw-extrabold text-warning mb-0">0</h2>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="medical-card p-4 border-0 shadow-sm">
                        <div class="text-muted extra-small text-uppercase fw-bold mb-1">High Risk Cases</div>
                        <h2 id="dashHigh" class="fw-extrabold text-danger mb-0">0</h2>
                    </div>
                </div>
            </div>

            <div class="medical-card p-4 mb-4 border-0 shadow-sm">
                <h5 class="fw-bold mb-3">Risk Distribution Breakdown</h5>
                <div class="progress mb-2" style="height: 18px; border-radius: 10px;">
                    <div id="barNormal" class="progress-bar bg-success" style="width: 0%"></div>
                    <div id="barMild" class="progress-bar bg-warning" style="width: 0%"></div>
                    <div id="barHigh" class="progress-bar bg-danger" style="width: 0%"></div>
                </div>
                <div class="d-flex justify-content-between small text-muted">
                    <span><i class="bi bi-circle-fill text-success me-1"></i> Normal</span>
                    <span><i class="bi bi-circle-fill text-warning me-1"></i> Mild Risk</span>
                    <span><i class="bi bi-circle-fill text-danger me-1"></i> High Risk</span>
                </div>
            </div>

            <div class="medical-card p-4 border-0 shadow-sm">
                <h5 class="fw-bold mb-3">Recent Screenings</h5>
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light extra-small text-uppercase">
                            <tr>
                                <th>#ID</th>
                                <th>Patient Name</th>
                                <th>Sensor Value</th>
                                <th>Status</th>
                                <th>Confidence</th>
                                <th>Timestamp</th>
                            </tr>
                        </thead>
                        <tbody id="recentTableBody">
                            <tr><td colspan="6" class="text-center py-4 text-muted">Loading recent logs...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- SECTION 4: HISTORY -->
    <div id="sec-history" class="section-block d-none py-5">
        <div class="container">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h2 class="fw-extrabold mb-1">Screening History & AI Dataset</h2>
                    <p class="text-muted mb-0">View all recorded screenings and export dataset CSV file.</p>
                </div>
                <a href="/export-dataset" class="btn btn-medical" target="_blank"><i class="bi bi-download me-1"></i> Export Dataset (CSV)</a>
            </div>

            <div class="medical-card p-4 mb-4 border-0 shadow-sm">
                <div class="row g-3 align-items-center mb-3">
                    <div class="col-md-6">
                        <input type="text" id="searchInput" class="form-control" placeholder="Search by patient name, status, or sensor value..." onkeyup="filterHistoryTable()">
                    </div>
                </div>

                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0" id="historyTable">
                        <thead class="table-light extra-small text-uppercase">
                            <tr>
                                <th>#ID</th>
                                <th>Patient Name</th>
                                <th>Age / Gender</th>
                                <th>Sensor Reading</th>
                                <th>Predicted Status</th>
                                <th>Confidence</th>
                                <th>Timestamp</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="historyTableBody">
                            <tr><td colspan="8" class="text-center py-4 text-muted">Loading history records...</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- SECTION 5: HARDWARE GUIDE -->
    <div id="sec-hardware" class="section-block d-none py-5">
        <div class="container">
            <div class="text-center max-w-3xl mx-auto mb-5">
                <h2 class="fw-extrabold mb-2">Hardware & AI Machine Learning Blueprint</h2>
                <p class="text-muted">Architecture for ESP32 optical sensor hardware & scikit-learn model training.</p>
            </div>
            <div class="row g-4">
                <div class="col-md-6">
                    <div class="medical-card p-4 h-100 border-0 shadow-sm">
                        <h4 class="fw-bold text-teal mb-3"><i class="bi bi-cpu me-2"></i> ESP32 Hardware Connection</h4>
                        <p class="text-muted small">Connect TCS34725 optical color sensor / LDR LED circuit to ESP32 ADC pin 34. Flash firmware from <code>hardware/esp32_sensor_node.ino</code>.</p>
                        <div class="bg-light p-3 rounded border font-monospace extra-small">
                            LED ---> Finger ---> Sensor ---> ESP32 ---> HTTP POST /api/predict
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="medical-card p-4 h-100 border-0 shadow-sm">
                        <h4 class="fw-bold text-teal mb-3"><i class="bi bi-robot me-2"></i> Machine Learning Transition</h4>
                        <p class="text-muted small">Once sensor dataset is exported via <code>/export-dataset</code>, train Random Forest classifier using <code>python ml/train_model.py</code>.</p>
                        <div class="bg-light p-3 rounded border font-monospace extra-small">
                            1. Export CSV -> 2. Label Bilirubin -> 3. Train Model -> 4. Deploy ml/predict.py
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="mt-auto bg-white border-top py-4 text-center text-muted small">
        <div class="container">
            Smart Jaundice Screening System &copy; 2026 Design Thinking Project.
        </div>
    </footer>

    <!-- Bootstrap 5 JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>

    <script>
        let allHistoryData = [];

        function showSection(secName) {
            document.querySelectorAll('.section-block').forEach(el => el.classList.add('d-none'));
            document.getElementById('sec-' + secName).classList.remove('d-none');
            if (secName === 'dashboard') loadDashboardData();
            if (secName === 'history') loadHistoryData();
        }

        function updateRangeVal(val) {
            document.getElementById('sensorRange').value = val;
            document.getElementById('sensorInput').value = val;
            document.getElementById('sliderValDisplay').innerText = val;
        }

        function setPresetVal(val) {
            updateRangeVal(val);
        }

        function randomScan() {
            const r = Math.floor(Math.random() * 256);
            updateRangeVal(r);
        }

        async function handleScreeningSubmit(e) {
            e.preventDefault();
            const sensor_value = parseInt(document.getElementById('sensorInput').value, 10);
            const name = document.getElementById('patientName').value;
            const age = document.getElementById('patientAge').value;
            const gender = document.getElementById('patientGender').value;

            try {
                const res = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sensor_value, name, age, gender })
                });
                const data = await res.json();
                renderResultCard(data);
            } catch (err) {
                alert('Error submitting screening: ' + err);
            }
        }

        function renderResultCard(data) {
            const cardBox = document.getElementById('resultCardBox');
            cardBox.classList.remove('d-none');

            const isNormal = data.status === 'Normal';
            const isMild = data.status === 'Mild Risk';
            const badgeBg = isNormal ? 'bg-success text-white' : isMild ? 'bg-warning text-dark' : 'bg-danger text-white';

            cardBox.innerHTML = `
                <div class="card border-0 shadow-lg rounded-4 overflow-hidden mt-4">
                    <div class="p-4 ${badgeBg}">
                        <h4 class="fw-bold mb-0"><i class="bi bi-shield-check me-2"></i> Screening Result: ${data.status}</h4>
                    </div>
                    <div class="card-body p-4">
                        <div class="row g-3 mb-3">
                            <div class="col-md-6">
                                <div class="text-muted extra-small text-uppercase fw-bold">Optical Sensor Reading</div>
                                <div class="display-6 fw-extrabold text-dark">${data.reading} / 255</div>
                            </div>
                            <div class="col-md-6">
                                <div class="text-muted extra-small text-uppercase fw-bold">Confidence Score</div>
                                <div class="display-6 fw-extrabold text-dark">${data.confidence}%</div>
                            </div>
                        </div>
                        <div class="alert ${isNormal ? 'alert-success' : isMild ? 'alert-warning' : 'alert-danger'} mb-0">
                            <strong>Recommendation:</strong> ${data.recommendation}
                        </div>
                    </div>
                </div>
            `;
        }

        async function loadDashboardData() {
            try {
                const res = await fetch('/api/statistics');
                const data = await res.json();

                document.getElementById('dashTotal').innerText = data.total_screenings;
                document.getElementById('dashNormal').innerText = data.normal_cases;
                document.getElementById('dashMild').innerText = data.mild_cases;
                document.getElementById('dashHigh').innerText = data.high_cases;

                const total = data.total_screenings || 1;
                document.getElementById('barNormal').style.width = ((data.normal_cases / total) * 100) + '%';
                document.getElementById('barMild').style.width = ((data.mild_cases / total) * 100) + '%';
                document.getElementById('barHigh').style.width = ((data.high_cases / total) * 100) + '%';

                const tbody = document.getElementById('recentTableBody');
                tbody.innerHTML = '';
                if (!data.recent_screenings || data.recent_screenings.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="6" class="text-center py-3 text-muted">No screenings recorded yet.</td></tr>';
                    return;
                }
                data.recent_screenings.forEach(s => {
                    const badgeClass = s.status === 'Normal' ? 'bg-success' : s.status === 'Mild Risk' ? 'bg-warning text-dark' : 'bg-danger';
                    tbody.innerHTML += `
                        <tr>
                            <td class="fw-bold text-muted">#${s.id}</td>
                            <td class="fw-semibold text-dark">${s.patient_name}</td>
                            <td><span class="badge bg-dark fs-6 px-3">${s.sensor_reading}</span></td>
                            <td><span class="badge ${badgeClass}">${s.status}</span></td>
                            <td class="fw-bold">${s.confidence}%</td>
                            <td class="small text-muted">${s.timestamp}</td>
                        </tr>
                    `;
                });
            } catch (err) {
                console.error(err);
            }
        }

        async function loadHistoryData() {
            try {
                const res = await fetch('/api/history');
                const data = await res.json();
                allHistoryData = data.history || [];
                renderHistoryRows(allHistoryData);
            } catch (err) {
                console.error(err);
            }
        }

        function renderHistoryRows(rows) {
            const tbody = document.getElementById('historyTableBody');
            tbody.innerHTML = '';
            if (rows.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-muted">No records found.</td></tr>';
                return;
            }
            rows.forEach(s => {
                const badgeClass = s.status === 'Normal' ? 'bg-success' : s.status === 'Mild Risk' ? 'bg-warning text-dark' : 'bg-danger';
                tbody.innerHTML += `
                    <tr>
                        <td class="fw-bold text-muted">#${s.id}</td>
                        <td class="fw-bold text-dark">${s.patient_name}</td>
                        <td class="small text-muted">${s.age} yrs / ${s.gender}</td>
                        <td><span class="badge bg-dark fs-6 px-3">${s.sensor_reading}</span></td>
                        <td><span class="badge ${badgeClass}">${s.status}</span></td>
                        <td class="fw-bold text-dark">${s.confidence}%</td>
                        <td class="small text-muted">${s.timestamp}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteHistoryRecord(${s.id})"><i class="bi bi-trash"></i> Delete</button>
                        </td>
                    </tr>
                `;
            });
        }

        function filterHistoryTable() {
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filtered = allHistoryData.filter(item => 
                item.patient_name.toLowerCase().includes(query) ||
                item.status.toLowerCase().includes(query) ||
                item.sensor_reading.toString().includes(query)
            );
            renderHistoryRows(filtered);
        }

        async function deleteHistoryRecord(id) {
            if (!confirm(`Delete record #${id}?`)) return;
            try {
                await fetch(`/api/record/${id}`, { method: 'DELETE' });
                loadHistoryData();
            } catch (err) {
                alert('Failed to delete: ' + err);
            }
        }
    </script>
</body>
</html>
"""

def create_app():
    """Flask Application Factory for Smart Jaundice Optical Screening System"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Create Database Tables Automatically
    with app.app_context():
        db.create_all()
        _seed_initial_data()

    # Ensure dataset output directory exists
    os.makedirs(app.config['DATASET_EXPORT_DIR'], exist_ok=True)

    # ------------------------------------------------------------------------
    # MVP Rule-Based Prediction Engine
    # Configurable Thresholds:
    # 100 - 255 = Normal
    # 70 - 99 = Mild Risk
    # 0 - 69 = High Risk
    # ------------------------------------------------------------------------
    def evaluate_sensor_reading(reading_val):
        """
        Rule-Based Risk Prediction Engine for Optical Sensor Value (0 - 255).
        Returns tuple: (status_label, confidence_score, clinical_recommendation)
        """
        normal_min = app.config['THRESHOLD_NORMAL_MIN']  # 100
        mild_min = app.config['THRESHOLD_MILD_MIN']      # 70

        if reading_val >= normal_min:
            status = "Normal"
            confidence = min(99.0, app.config['BASE_CONFIDENCE_NORMAL'] + ((reading_val - normal_min) / 155.0) * 8.0)
            recommendation = "Optical sensor reading is within healthy limits. No evidence of jaundice detected."
        elif reading_val >= mild_min:
            status = "Mild Risk"
            confidence = min(95.0, app.config['BASE_CONFIDENCE_MILD'] + ((99 - reading_val) / 30.0) * 10.0)
            recommendation = "Borderline optical reading detected. Monitor for yellowing of sclera/skin and re-test in 24 hours."
        else:
            status = "High Risk"
            confidence = min(98.0, app.config['BASE_CONFIDENCE_HIGH'] + ((69 - reading_val) / 69.0) * 6.0)
            recommendation = "Please consult a healthcare professional for further evaluation and serum bilirubin testing."

        return status, round(confidence, 1), recommendation

    # ------------------------------------------------------------------------
    # FRONTEND ROUTE - Renders Web App Interface
    # ------------------------------------------------------------------------

    @app.route('/', methods=['GET'])
    def home_ui():
        """Serves full interactive medical web application directly"""
        return render_template_string(UI_TEMPLATE)

    # ------------------------------------------------------------------------
    # REST API ENDPOINTS
    # ------------------------------------------------------------------------

    # 1. POST /predict or /api/predict
    @app.route('/predict', methods=['POST'])
    @app.route('/api/predict', methods=['POST'])
    def predict():
        data = request.get_json() or {}

        sensor_val_raw = data.get('sensor_value', data.get('reading', None))
        if sensor_val_raw is None:
            return jsonify({'error': 'Missing required field: "sensor_value" (Range 0 - 255)'}), 400

        try:
            sensor_value = int(sensor_val_raw)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid "sensor_value". Must be an integer between 0 and 255.'}), 400

        if not (0 <= sensor_value <= 255):
            return jsonify({'error': '"sensor_value" must be in the range 0 to 255.'}), 400

        patient_name = data.get('name', 'Anonymous Patient').strip() or 'Anonymous Patient'
        patient_age = data.get('age', 0)
        try:
            patient_age = int(patient_age) if patient_age else 0
        except (ValueError, TypeError):
            patient_age = 0
        patient_gender = data.get('gender', 'Unspecified').strip() or 'Unspecified'

        status, confidence, recommendation = evaluate_sensor_reading(sensor_value)

        try:
            patient = Patient(
                name=patient_name,
                age=patient_age,
                gender=patient_gender
            )
            db.session.add(patient)
            db.session.flush()

            screening = Screening(
                patient_id=patient.id,
                sensor_reading=sensor_value,
                status=status,
                confidence_score=confidence,
                recommendation=recommendation
            )
            db.session.add(screening)
            db.session.commit()

            return jsonify({
                "id": screening.id,
                "reading": sensor_value,
                "sensor_value": sensor_value,
                "status": status,
                "confidence": confidence,
                "confidence_score": confidence,
                "recommendation": recommendation,
                "patient": patient.to_dict(),
                "timestamp": screening.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to record screening: {str(e)}'}), 500

    # 2. GET /history or /api/history
    @app.route('/history', methods=['GET'])
    @app.route('/api/history', methods=['GET'])
    def get_history():
        screenings = Screening.query.order_by(Screening.timestamp.desc()).all()
        return jsonify({
            'count': len(screenings),
            'history': [s.to_dict() for s in screenings]
        }), 200

    # 3. GET /statistics or /api/statistics
    @app.route('/statistics', methods=['GET'])
    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        all_screenings = Screening.query.all()
        total_screenings = len(all_screenings)

        normal_cases = sum(1 for s in all_screenings if s.status == 'Normal')
        mild_cases = sum(1 for s in all_screenings if s.status == 'Mild Risk')
        high_cases = sum(1 for s in all_screenings if s.status == 'High Risk')

        avg_reading = (sum(s.sensor_reading for s in all_screenings) / total_screenings) if total_screenings > 0 else 0
        avg_confidence = (sum(s.confidence_score for s in all_screenings) / total_screenings) if total_screenings > 0 else 0

        recent_screenings = [s.to_dict() for s in all_screenings[-5:][::-1]]

        return jsonify({
            'total_screenings': total_screenings,
            'normal_cases': normal_cases,
            'mild_cases': mild_cases,
            'high_cases': high_cases,
            'avg_sensor_reading': round(avg_reading, 1),
            'avg_confidence': round(avg_confidence, 1),
            'recent_screenings': recent_screenings
        }), 200

    # 4. GET /export-dataset or /api/export-dataset
    @app.route('/export-dataset', methods=['GET'])
    @app.route('/api/export-dataset', methods=['GET'])
    def export_dataset():
        screenings = Screening.query.order_by(Screening.id.asc()).all()

        csv_filename = 'jaundice_optical_dataset.csv'
        csv_file_path = os.path.join(app.config['DATASET_EXPORT_DIR'], csv_filename)

        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['patient_id', 'age', 'gender', 'sensor_reading', 'predicted_status', 'timestamp'])
            for s in screenings:
                writer.writerow([
                    s.patient_id,
                    s.patient.age if s.patient else 0,
                    s.patient.gender if s.patient else 'Unspecified',
                    s.sensor_reading,
                    s.status,
                    s.timestamp.strftime('%Y-%m-%d %H:%M:%S') if s.timestamp else ''
                ])

        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(['patient_id', 'age', 'gender', 'sensor_reading', 'predicted_status', 'timestamp'])
        for s in screenings:
            writer.writerow([
                s.patient_id,
                s.patient.age if s.patient else 0,
                s.patient.gender if s.patient else 'Unspecified',
                s.sensor_reading,
                s.status,
                s.timestamp.strftime('%Y-%m-%d %H:%M:%S') if s.timestamp else ''
            ])

        response = Response(output_buffer.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={csv_filename}'
        return response

    # 5. DELETE /record/<id> or /api/record/<id>
    @app.route('/record/<int:record_id>', methods=['DELETE'])
    @app.route('/api/record/<int:record_id>', methods=['DELETE'])
    def delete_record(record_id):
        screening = Screening.query.get(record_id)
        if not screening:
            return jsonify({'error': f'Record #{record_id} not found.'}), 404

        try:
            patient_id = screening.patient_id
            db.session.delete(screening)
            
            if Screening.query.filter_by(patient_id=patient_id).count() == 1:
                patient = Patient.query.get(patient_id)
                if patient:
                    db.session.delete(patient)

            db.session.commit()
            return jsonify({'message': f'Screening record #{record_id} deleted successfully.'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete record: {str(e)}'}), 500

    return app

def _seed_initial_data():
    if Screening.query.count() == 0:
        sample_patients = [
            Patient(name='Sample Patient A', age=30, gender='Female'),
            Patient(name='Sample Patient B', age=54, gender='Male'),
            Patient(name='Sample Patient C', age=5, gender='Child')
        ]
        db.session.add_all(sample_patients)
        db.session.flush()

        sample_screenings = [
            Screening(patient_id=sample_patients[0].id, sensor_reading=185, status='Normal', confidence_score=94.5, recommendation='Optical sensor reading is within healthy limits. No evidence of jaundice detected.'),
            Screening(patient_id=sample_patients[1].id, sensor_reading=85, status='Mild Risk', confidence_score=82.0, recommendation='Borderline optical reading detected. Monitor for yellowing of sclera/skin and re-test in 24 hours.'),
            Screening(patient_id=sample_patients[2].id, sensor_reading=42, status='High Risk', confidence_score=92.5, recommendation='Please consult a healthcare professional for further evaluation and serum bilirubin testing.')
        ]
        db.session.add_all(sample_screenings)
        db.session.commit()
        print("[INFO] Seeded sample optical sensor screening data.")

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[SUCCESS] Smart Jaundice Optical Screening API running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
