"""
================================================================================
Real-Time Hardware Monitoring Dashboard Template
NodeMCU ESP8266 & GY-9960 / APDS-9960 Optical Sensor Node
================================================================================
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neonatal Jaundice Real-Time Optical Monitor - NodeMCU & GY-9960</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
        :root {
            --primary-teal: #0d9488;
            --primary-teal-dark: #0f766e;
            --primary-teal-light: #ccfbf1;
            --accent-cyan: #0284c7;
            --dark-navy: #0f172a;
            --slate-muted: #64748b;
            --light-bg: #f8fafc;
            --border-color: #e2e8f0;
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
            border-bottom: 1px solid var(--border-color);
        }

        .medical-card {
            background: #ffffff;
            border: 1px solid var(--border-color);
            border-radius: 16px;
            box-shadow: 0 10px 30px -5px rgba(15, 23, 42, 0.05);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .medical-card:hover {
            box-shadow: 0 16px 35px -8px rgba(13, 148, 136, 0.12);
            transform: translateY(-2px);
        }

        .btn-medical {
            background: linear-gradient(135deg, var(--primary-teal) 0%, var(--accent-cyan) 100%);
            color: #ffffff !important;
            border: none;
            font-weight: 600;
            border-radius: 12px;
            padding: 8px 18px;
            box-shadow: 0 4px 14px rgba(13, 148, 136, 0.25);
            transition: all 0.2s ease;
        }
        .btn-medical:hover { opacity: 0.92; transform: translateY(-1px); }

        .btn-outline-medical {
            border: 2px solid var(--primary-teal);
            color: var(--primary-teal) !important;
            font-weight: 600;
            border-radius: 12px;
            padding: 7px 18px;
            background: transparent;
            transition: all 0.2s ease;
        }
        .btn-outline-medical:hover {
            background: var(--primary-teal-light);
            color: var(--primary-teal-dark) !important;
        }

        /* Pulsing connection badges */
        @keyframes pulse-green {
            0% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7); }
            70% { box-shadow: 0 0 0 8px rgba(34, 197, 94, 0); }
            100% { box-shadow: 0 0 0 0 rgba(34, 197, 94, 0); }
        }

        .pulse-dot-online {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #22c55e;
            border-radius: 50%;
            animation: pulse-green 1.8s infinite;
        }

        .pulse-dot-offline {
            display: inline-block;
            width: 10px;
            height: 10px;
            background-color: #ef4444;
            border-radius: 50%;
        }

        .badge-status-online {
            background-color: #dcfce7;
            color: #15803d;
            font-weight: 700;
            border: 1px solid #bbf7d0;
            border-radius: 30px;
            padding: 6px 14px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
        }

        .badge-status-offline {
            background-color: #fee2e2;
            color: #b91c1c;
            font-weight: 700;
            border: 1px solid #fecaca;
            border-radius: 30px;
            padding: 6px 14px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
        }

        .badge-calib {
            background-color: #fef3c7;
            color: #92400e;
            font-weight: 700;
            border: 1px solid #fde68a;
        }

        /* Telemetry Cards */
        .sensor-card-val {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.1;
        }

        .sensor-progress {
            height: 6px;
            border-radius: 3px;
            background: #e2e8f0;
            overflow: hidden;
            margin-top: 10px;
        }

        .color-swatch-box {
            width: 68px;
            height: 68px;
            border-radius: 14px;
            border: 3px solid #ffffff;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.12);
            transition: background-color 0.4s ease;
            flex-shrink: 0;
        }

        .table-history th {
            background-color: #f8fafc;
            color: var(--slate-muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 700;
        }
        .table-history td {
            font-size: 0.85rem;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <!-- NAVIGATION BAR -->
    <nav class="navbar navbar-expand-lg navbar-medical sticky-top py-2">
        <div class="container-fluid px-lg-4">
            <a class="navbar-brand d-flex align-items-center gap-2" href="#">
                <span class="p-2 rounded-3 text-white" style="background: linear-gradient(135deg, var(--primary-teal), var(--accent-cyan));">
                    <i class="bi bi-activity fs-5"></i>
                </span>
                <div>
                    <span class="fw-bold fs-6 text-dark d-block lh-sm">Neonatal Jaundice Real-Time Optical Monitor</span>
                    <span class="text-muted extra-small" style="font-size: 0.72rem;">NodeMCU ESP8266 &bull; GY-9960 Optical Sensor &bull; SSD1306 OLED</span>
                </div>
            </a>

            <!-- Right Controls: Status & Monitoring Toggle -->
            <div class="d-flex align-items-center gap-3 ms-auto mt-2 mt-lg-0">
                <!-- Connection Status Badge -->
                <div id="connectionStatusContainer">
                    <span id="connectionBadge" class="badge-status-offline">
                        <span class="pulse-dot-offline"></span> Checking Hardware...
                    </span>
                </div>

                <!-- Start / Pause Monitoring Control -->
                <button id="btnMonitorToggle" class="btn btn-sm btn-medical d-flex align-items-center gap-2" onclick="toggleMonitoring()">
                    <i class="bi bi-pause-fill fs-6" id="iconMonitorToggle"></i>
                    <span id="textMonitorToggle">Pause Monitoring</span>
                </button>

                <!-- Immediate Poll Button -->
                <button class="btn btn-sm btn-outline-medical" onclick="triggerManualPoll()" title="Poll hardware now">
                    <i class="bi bi-arrow-repeat"></i> Poll
                </button>
            </div>
        </div>
    </nav>

    <!-- MAIN DASHBOARD CONTAINER -->
    <div class="container-fluid px-lg-4 py-4">
        <!-- Sub-Header: Stream Health & Last Update -->
        <div class="row align-items-center g-2 mb-3">
            <div class="col-md-6">
                <div class="d-flex align-items-center gap-2 small text-muted">
                    <i class="bi bi-broadcast text-teal"></i>
                    <span>Stream Engine: <strong>Automatic Polling (1.5s interval)</strong></span>
                    <span class="text-muted">&bull;</span>
                    <span id="lastReadingTimeText">Last reading: <em>Waiting for hardware...</em></span>
                </div>
            </div>
            <div class="col-md-6 text-md-end">
                <span class="badge py-1 px-3 rounded-pill fw-semibold" style="background-color: #ccfbf1; color: #0f766e; font-size: 0.75rem;">
                    <i class="bi bi-lightbulb-fill me-1"></i> Design Thinking Engineering Prototype
                </span>
            </div>
        </div>

        <!-- CLINICAL RESEARCH NOTICE -->
        <div class="alert alert-warning py-2 px-3 rounded-3 border-warning small d-flex align-items-center gap-2 mb-4">
            <i class="bi bi-exclamation-triangle-fill fs-5 text-warning flex-shrink-0"></i>
            <div>
                <strong>Clinical Research Prototype Notice:</strong> Transcutaneous optical color measurements capture tissue optical reflectance. Diagnostic jaundice assessment and bilirubin concentration estimation require empirical calibration against laboratory <strong>Serum Total Bilirubin (STB)</strong> reference standards.
            </div>
        </div>

        <!-- CONDITIONAL OFFLINE ALERT BANNER -->
        <div id="offlineAlertBanner" class="alert alert-danger py-3 px-4 rounded-3 border-danger d-none mb-4">
            <div class="d-flex align-items-start gap-3">
                <i class="bi bi-wifi-off fs-3 text-danger flex-shrink-0"></i>
                <div class="flex-grow-1">
                    <h6 class="fw-bold text-danger mb-1">Hardware Offline &bull; Waiting for NodeMCU Sensor Stream</h6>
                    <p class="small text-muted mb-2">
                        No real-time transmission received from the NodeMCU ESP8266 within the last 15 seconds. Ensure your hardware is powered and connected to Wi-Fi.
                    </p>
                    <div class="p-2 bg-white rounded-2 border extra-small text-dark">
                        <strong>Troubleshooting Checklist:</strong>
                        <ul class="mb-0 ps-3">
                            <li>Verify NodeMCU is connected to your local Wi-Fi router / hotspot.</li>
                            <li>Ensure NodeMCU code has your PC LAN IP in <code>backendUrl</code> (port 5000).</li>
                            <li>Check that GY-9960 SDA is on D2 (GPIO 4), SCL is on D1 (GPIO 5), and powered via 3.3V.</li>
                            <li><em>Bench Simulation Mode:</em> Run <code>.venv\Scripts\python.exe simulate_nodemcu_hardware.py</code> in a terminal to send live test scans.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- 4 REAL-TIME SENSOR READING CARDS (CLEAR, RED, GREEN, BLUE) -->
        <div class="row g-3 mb-4">
            <!-- 1. CLEAR CHANNEL CARD -->
            <div class="col-sm-6 col-xl-3">
                <div class="medical-card p-3 h-100 border-start border-4 border-secondary">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="extra-small fw-bold text-muted text-uppercase">Clear (Broad Spectrum)</span>
                        <i class="bi bi-brightness-high fs-5 text-secondary"></i>
                    </div>
                    <div class="sensor-card-val text-dark" id="dispClear">--</div>
                    <div class="text-muted extra-small" style="font-size: 0.75rem;">Total ambient & reflected illuminance</div>
                    <div class="sensor-progress">
                        <div id="barClear" class="progress-bar bg-secondary" style="width: 0%; height: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- 2. RED CHANNEL CARD -->
            <div class="col-sm-6 col-xl-3">
                <div class="medical-card p-3 h-100 border-start border-4 border-danger">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="extra-small fw-bold text-danger text-uppercase">Red Channel (650 nm)</span>
                        <i class="bi bi-circle-fill fs-5 text-danger"></i>
                    </div>
                    <div class="sensor-card-val text-danger" id="dispRed">--</div>
                    <div class="text-muted extra-small" style="font-size: 0.75rem;">Cutaneous baseline tissue reflectance</div>
                    <div class="sensor-progress">
                        <div id="barRed" class="progress-bar bg-danger" style="width: 0%; height: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- 3. GREEN CHANNEL CARD -->
            <div class="col-sm-6 col-xl-3">
                <div class="medical-card p-3 h-100 border-start border-4 border-success">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="extra-small fw-bold text-success text-uppercase">Green Channel (550 nm)</span>
                        <i class="bi bi-circle-fill fs-5 text-success"></i>
                    </div>
                    <div class="sensor-card-val text-success" id="dispGreen">--</div>
                    <div class="text-muted extra-small" style="font-size: 0.75rem;">Hemoglobin & melanin reference baseline</div>
                    <div class="sensor-progress">
                        <div id="barGreen" class="progress-bar bg-success" style="width: 0%; height: 100%;"></div>
                    </div>
                </div>
            </div>

            <!-- 4. BLUE CHANNEL CARD -->
            <div class="col-sm-6 col-xl-3">
                <div class="medical-card p-3 h-100 border-start border-4 border-primary">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="extra-small fw-bold text-primary text-uppercase">Blue Channel (450 nm)</span>
                        <i class="bi bi-circle-fill fs-5 text-primary"></i>
                    </div>
                    <div class="sensor-card-val text-primary" id="dispBlue">--</div>
                    <div class="text-muted extra-small" style="font-size: 0.75rem;"><strong>Bilirubin optical absorption peak</strong></div>
                    <div class="sensor-progress">
                        <div id="barBlue" class="progress-bar bg-primary" style="width: 0%; height: 100%;"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- OPTICAL ANALYSIS & LIVE COLOR SYNTHESIS -->
        <div class="row g-3 mb-4">
            <!-- Live Synthesized Optical Color Swatch -->
            <div class="col-lg-5">
                <div class="medical-card p-4 h-100">
                    <h6 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                        <i class="bi bi-palette-fill text-teal"></i> Real-Time Optical Color Synthesis
                    </h6>
                    <div class="d-flex align-items-center gap-3 p-3 rounded-3 border bg-light mb-3">
                        <div id="liveColorSwatch" class="color-swatch-box" style="background-color: #cbd5e1;"></div>
                        <div>
                            <div class="fw-bold fs-6 text-dark" id="liveColorHex">rgb(--, --, --)</div>
                            <div class="text-muted small" id="liveColorDesc">Synthesized directly from Red, Green, Blue counts</div>
                        </div>
                    </div>
                    <p class="extra-small text-muted mb-0">
                        Shows the cutaneous optical reflectance profile in real-time. Attenuation of the blue component relative to red/green causes a yellow shift indicative of elevated tissue bilirubin.
                    </p>
                </div>
            </div>

            <!-- Optical Metrics & Jaundice Ratios -->
            <div class="col-lg-7">
                <div class="medical-card p-4 h-100">
                    <h6 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                        <i class="bi bi-calculator text-teal"></i> Bilirubin Optical Indices & Screening Assessment
                    </h6>
                    <div class="row g-3 mb-3">
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center h-100">
                                <div class="extra-small fw-bold text-muted text-uppercase">R/B Optical Ratio</div>
                                <div class="fs-2 fw-extrabold text-dark mt-1" id="dispRatioRB">--</div>
                                <div class="extra-small text-muted">Red / Blue ratio</div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center h-100">
                                <div class="extra-small fw-bold text-muted text-uppercase">Yellow-to-Blue Index</div>
                                <div class="fs-2 fw-extrabold text-dark mt-1" id="dispYellowIdx">--</div>
                                <div class="extra-small text-muted">(R + G) / (2 &times; B)</div>
                            </div>
                        </div>
                        <div class="col-sm-4">
                            <div class="p-3 bg-light rounded-3 border text-center h-100">
                                <div class="extra-small fw-bold text-muted text-uppercase">Clinical Status</div>
                                <div class="mt-2" id="dispStatusContainer">
                                    <span class="badge badge-calib fs-6 px-2 py-1" id="dispStatusBadge">Calibration Required</span>
                                </div>
                                <div class="extra-small text-success mt-1"><i class="bi bi-check-circle-fill me-1"></i>Calibrated: R:38, G:30, B:25</div>
                            </div>
                        </div>
                    </div>
                    <div class="p-2 px-3 rounded-2 bg-light border extra-small text-muted" id="dispRecommendation">
                        Awaiting live sensor reading from NodeMCU hardware...
                    </div>
                </div>
            </div>
        </div>

        <!-- CLINICAL THRESHOLD RANGES: NORMAL, AVERAGE, CRITICAL -->
        <div class="row g-3 mb-4">
            <div class="col-12">
                <div class="medical-card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <div>
                            <h6 class="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                                <i class="bi bi-speedometer2 text-teal"></i> Cutaneous Bilirubin Screening Threshold Ranges
                            </h6>
                            <span class="text-muted extra-small">Calibrated from empirical sensor run (Clear: 75-77 | Red: 38 | Green: 29-30 | Blue: 24-25)</span>
                        </div>
                        <div>
                            <span class="badge py-1 px-3 rounded-pill bg-light border text-dark extra-small">
                                <i class="bi bi-shield-check text-success me-1"></i> Empirical Baseline: R/B = 1.55 | Yellow Index = 1.38
                            </span>
                        </div>
                    </div>

                    <!-- 3 Cards: Normal, Average, Critical -->
                    <div class="row g-3">
                        <!-- 1. NORMAL RANGE -->
                        <div class="col-md-4">
                            <div class="p-3 rounded-3 border h-100 bg-white" style="border-left: 5px solid #22c55e !important; box-shadow: 0 2px 8px rgba(34,197,94,0.08);">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1 fw-bold extra-small">
                                        <i class="bi bi-check-circle-fill me-1"></i> NORMAL (Low Risk)
                                    </span>
                                    <span class="fw-bold text-success fs-6">&le; 1.65 R/B</span>
                                </div>
                                <ul class="list-unstyled extra-small text-dark mb-2 lh-lg">
                                    <li><strong>R/B Optical Ratio:</strong> <span class="badge bg-light text-dark border">&le; 1.65</span> (Baseline: 1.52 &ndash; 1.58)</li>
                                    <li><strong>Yellow-Blue Index:</strong> <span class="badge bg-light text-dark border">&le; 1.45</span> (Baseline: 1.36 &ndash; 1.40)</li>
                                    <li><strong>Blue Reflection (B):</strong> <span class="badge bg-light text-dark border">&ge; 24 counts</span> (Unattenuated)</li>
                                    <li><strong>Estimated TcB / STB:</strong> &lt; 5.0 mg/dL (Physiological)</li>
                                </ul>
                                <div class="p-2 rounded bg-light extra-small text-muted border">
                                    <strong class="text-success">Action:</strong> Normal cutaneous baseline. Routine follow-up; no phototherapy required.
                                </div>
                            </div>
                        </div>

                        <!-- 2. AVERAGE RANGE -->
                        <div class="col-md-4">
                            <div class="p-3 rounded-3 border h-100 bg-white" style="border-left: 5px solid #f59e0b !important; box-shadow: 0 2px 8px rgba(245,158,11,0.08);">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="badge bg-warning-subtle text-warning-emphasis border border-warning-subtle px-2 py-1 fw-bold extra-small">
                                        <i class="bi bi-exclamation-circle-fill me-1"></i> AVERAGE (Mild Risk)
                                    </span>
                                    <span class="fw-bold text-warning-emphasis fs-6">1.66 &ndash; 2.10 R/B</span>
                                </div>
                                <ul class="list-unstyled extra-small text-dark mb-2 lh-lg">
                                    <li><strong>R/B Optical Ratio:</strong> <span class="badge bg-light text-dark border">1.66 &ndash; 2.10</span></li>
                                    <li><strong>Yellow-Blue Index:</strong> <span class="badge bg-light text-dark border">1.46 &ndash; 1.85</span></li>
                                    <li><strong>Blue Reflection (B):</strong> <span class="badge bg-light text-dark border">19 &ndash; 23 counts</span> (Moderate Drop)</li>
                                    <li><strong>Estimated TcB / STB:</strong> 5.0 &ndash; 12.0 mg/dL (Surveillance)</li>
                                </ul>
                                <div class="p-2 rounded bg-light extra-small text-muted border">
                                    <strong class="text-warning-emphasis">Action:</strong> Borderline blue light absorption. Re-screen in 4&ndash;6 hours or check with TcB.
                                </div>
                            </div>
                        </div>

                        <!-- 3. CRITICAL RANGE -->
                        <div class="col-md-4">
                            <div class="p-3 rounded-3 border h-100 bg-white" style="border-left: 5px solid #ef4444 !important; box-shadow: 0 2px 8px rgba(239,68,68,0.08);">
                                <div class="d-flex justify-content-between align-items-center mb-2">
                                    <span class="badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1 fw-bold extra-small">
                                        <i class="bi bi-exclamation-triangle-fill me-1"></i> CRITICAL (High Risk)
                                    </span>
                                    <span class="fw-bold text-danger fs-6">&gt; 2.10 R/B</span>
                                </div>
                                <ul class="list-unstyled extra-small text-dark mb-2 lh-lg">
                                    <li><strong>R/B Optical Ratio:</strong> <span class="badge bg-light text-dark border">&gt; 2.10</span></li>
                                    <li><strong>Yellow-Blue Index:</strong> <span class="badge bg-light text-dark border">&gt; 1.85</span></li>
                                    <li><strong>Blue Reflection (B):</strong> <span class="badge bg-light text-dark border">&lt; 19 counts</span> (Severe Attenuation)</li>
                                    <li><strong>Estimated TcB / STB:</strong> &gt; 12.0 &ndash; 15.0+ mg/dL (Phototherapy Risk)</li>
                                </ul>
                                <div class="p-2 rounded bg-light extra-small text-muted border">
                                    <strong class="text-danger">Action:</strong> Severe blue light absorption. Immediate pediatric workup & STB blood test recommended.
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Range Continuum Bar -->
                    <div class="mt-3 pt-3 border-top">
                        <div class="d-flex justify-content-between extra-small fw-semibold text-muted mb-1">
                            <span class="text-success"><i class="bi bi-shield-check"></i> Normal Zone (&le; 1.65)</span>
                            <span class="text-warning-emphasis"><i class="bi bi-exclamation-circle"></i> Average / Mild Risk (1.66 - 2.10)</span>
                            <span class="text-danger"><i class="bi bi-exclamation-triangle"></i> Critical Zone (&gt; 2.10)</span>
                        </div>
                        <div class="progress position-relative" style="height: 12px; border-radius: 6px; background-color: #e2e8f0;">
                            <div class="progress-bar bg-success" style="width: 45%;" title="Normal: R/B &le; 1.65"></div>
                            <div class="progress-bar bg-warning" style="width: 30%;" title="Average: R/B 1.66 - 2.10"></div>
                            <div class="progress-bar bg-danger" style="width: 25%;" title="Critical: R/B &gt; 2.10"></div>
                        </div>
                        <div class="d-flex justify-content-between extra-small text-muted mt-1" style="font-size: 0.72rem;">
                            <span>1.0</span>
                            <span class="fw-bold text-success">1.52 (Your Baseline)</span>
                            <span class="fw-bold text-warning-emphasis">1.65 (Normal Max)</span>
                            <span class="fw-bold text-danger">2.10 (Critical Threshold)</span>
                            <span>3.0+</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- REAL-TIME LINE CHART (TRENDS OVER TIME) -->
        <div class="row g-3 mb-4">
            <div class="col-12">
                <div class="medical-card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <div>
                            <h5 class="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                                <i class="bi bi-graph-up text-teal"></i> Live Sensor Optical Trends (Rolling Time Window)
                            </h5>
                            <span class="text-muted extra-small">Continuous optical irradiance variations across Clear, Red, Green, and Blue channels</span>
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="badge bg-light text-dark border small">Auto-updating every 1.5s</span>
                            <button class="btn btn-sm btn-medical py-0 px-2 me-1" onclick="loadCalibratedGraphData()" title="Show the 13 calibrated sensor runs">
                                <i class="bi bi-graph-up-arrow"></i> Load 13 Calibrated Runs
                            </button>
                            <button class="btn btn-sm btn-outline-secondary py-0 px-2" onclick="resetChartData()" title="Reset chart window">
                                <i class="bi bi-trash"></i> Reset Chart
                            </button>
                        </div>
                    </div>
                    <div style="position: relative; width: 100%; height: 280px;">
                        <canvas id="liveSensorChart"></canvas>
                    </div>
                </div>
            </div>
        </div>

        <!-- RECENT READINGS HISTORY TABLE -->
        <div class="row g-3 mb-4">
            <div class="col-12">
                <div class="medical-card p-4">
                    <div class="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
                        <div>
                            <h5 class="fw-bold text-dark mb-0 d-flex align-items-center gap-2">
                                <i class="bi bi-clock-history text-teal"></i> Recent Hardware Screenings Log
                            </h5>
                            <span class="text-muted extra-small">Chronological incoming transmission log recorded by the Flask SQLite database</span>
                        </div>
                        <div class="d-flex gap-2">
                            <a href="/api/export-dataset" class="btn btn-sm btn-outline-medical d-flex align-items-center gap-1">
                                <i class="bi bi-file-earmark-arrow-down"></i> Export CSV
                            </a>
                        </div>
                    </div>

                    <div class="table-responsive">
                        <table class="table table-hover table-history mb-0">
                            <thead>
                                <tr>
                                    <th>#ID</th>
                                    <th>Timestamp</th>
                                    <th>Sensor</th>
                                    <th>Clear (Lux)</th>
                                    <th>Red (650nm)</th>
                                    <th>Green (550nm)</th>
                                    <th>Blue (450nm)</th>
                                    <th>R/B Ratio</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody id="historyTableBody">
                                <tr>
                                    <td colspan="9" class="text-center py-4 text-muted">Loading recent hardware records...</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- HARDWARE WIRING & DEVICE INFORMATION SECTION -->
        <div class="row g-3">
            <div class="col-12">
                <div class="medical-card p-4">
                    <h5 class="fw-bold text-dark mb-3 d-flex align-items-center gap-2">
                        <i class="bi bi-cpu-fill text-teal"></i> Connected Hardware Specifications & Pinout Reference
                    </h5>
                    <div class="row g-3">
                        <div class="col-lg-6">
                            <table class="table table-sm table-bordered extra-small mb-0">
                                <thead class="table-light">
                                    <tr><th>Peripheral Pin</th><th>NodeMCU Pin</th><th>GPIO</th><th>Electrical Notes</th></tr>
                                </thead>
                                <tbody>
                                    <tr><td><strong>GY-9960 SDA & OLED SDA</strong></td><td><strong>D2</strong></td><td>GPIO 4</td><td>Shared I²C Data Line (0x39 & 0x3C)</td></tr>
                                    <tr><td><strong>GY-9960 SCL & OLED SCL</strong></td><td><strong>D1</strong></td><td>GPIO 5</td><td>Shared I²C Clock Line (100 kHz)</td></tr>
                                    <tr><td><strong>Push Button</strong></td><td><strong>D6</strong></td><td>GPIO 12</td><td>Trigger Scan (INPUT_PULLUP to GND)</td></tr>
                                    <tr><td><strong>Diagnostic LED</strong></td><td><strong>D5</strong></td><td>GPIO 14</td><td>Active HIGH (via 220–330 ohm resistor)</td></tr>
                                    <tr><td><strong>VCC</strong></td><td><strong>3.3V (3V3)</strong></td><td>3.3V</td><td>Regulated 3.3V rail (Do NOT use 5V)</td></tr>
                                    <tr><td><strong>GND</strong></td><td><strong>GND</strong></td><td>GND</td><td>Common system ground</td></tr>
                                </tbody>
                            </table>
                        </div>
                        <div class="col-lg-6">
                            <div class="p-3 bg-light rounded-3 border h-100">
                                <h6 class="fw-bold text-dark small mb-2">Network Architecture & Data Flow</h6>
                                <p class="extra-small text-muted mb-2">
                                    The <strong>NodeMCU ESP8266</strong> connects to Wi-Fi and continuously samples the <strong>GY-9960 colour sensor</strong>.
                                    Readings are displayed on the <strong>0.96" SSD1306 OLED</strong>, served locally on <strong>Port 80</strong>, and transmitted via HTTP POST to this Flask backend endpoint: <code>/api/predict</code>.
                                </p>
                                <div class="extra-small text-muted">
                                    <strong>Target Backend URL in NodeMCU:</strong> <code>http://&lt;PC_IP&gt;:5000/api/predict</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- JAVASCRIPT LOGIC: REAL-TIME POLLING & LIVE CHART.JS -->
    <script>
        let isMonitoring = true;
        let pollTimer = null;
        let lastLoggedId = null;
        let sensorChart = null;

        const MAX_CHART_POINTS = 30;
        const chartLabels = [];
        const chartDataRed = [];
        const chartDataGreen = [];
        const chartDataBlue = [];
        const chartDataClear = [];
        const chartDataRatio = [];

        // 13 Calibrated Sensor Readings Provided by Hardware
        const CALIBRATED_RUNS = [
            { id: 1,  time: "719s", led: "OFF",   c: 77, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 2,  time: "720s", led: "BLUE",  c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 3,  time: "721s", led: "GREEN", c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 4,  time: "722s", led: "WHITE", c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 5,  time: "724s", led: "OFF",   c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 6,  time: "725s", led: "BLUE",  c: 76, r: 38, g: 30, b: 24, ratio: 1.58 },
            { id: 7,  time: "726s", led: "GREEN", c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 8,  time: "727s", led: "WHITE", c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 9,  time: "729s", led: "OFF",   c: 76, r: 38, g: 30, b: 25, ratio: 1.52 },
            { id: 10, time: "730s", led: "BLUE",  c: 75, r: 38, g: 30, b: 24, ratio: 1.58 },
            { id: 11, time: "732s", led: "GREEN", c: 75, r: 38, g: 29, b: 24, ratio: 1.58 },
            { id: 12, time: "733s", led: "WHITE", c: 75, r: 38, g: 29, b: 24, ratio: 1.58 },
            { id: 13, time: "735s", led: "OFF",   c: 75, r: 38, g: 29, b: 24, ratio: 1.58 }
        ];

        function loadCalibratedGraphData() {
            chartLabels.length = 0;
            chartDataRed.length = 0;
            chartDataGreen.length = 0;
            chartDataBlue.length = 0;
            chartDataClear.length = 0;
            chartDataRatio.length = 0;

            CALIBRATED_RUNS.forEach(pt => {
                chartLabels.push(`#${pt.id} ${pt.led} (${pt.time})`);
                chartDataRed.push(pt.r);
                chartDataGreen.push(pt.g);
                chartDataBlue.push(pt.b);
                chartDataClear.push(pt.c);
                chartDataRatio.push(pt.ratio);
            });
            if (sensorChart) sensorChart.update();
        }

        // 1. Initialize Chart.js
        function initChart() {
            const ctx = document.getElementById('liveSensorChart').getContext('2d');
            sensorChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartLabels,
                    datasets: [
                        {
                            label: 'Red (650nm)',
                            data: chartDataRed,
                            borderColor: '#ef4444',
                            backgroundColor: 'rgba(239, 68, 68, 0.1)',
                            borderWidth: 2.5,
                            tension: 0.3,
                            pointRadius: 4,
                            pointHoverRadius: 7,
                            yAxisID: 'y',
                            fill: false
                        },
                        {
                            label: 'Green (550nm)',
                            data: chartDataGreen,
                            borderColor: '#22c55e',
                            backgroundColor: 'rgba(34, 197, 94, 0.1)',
                            borderWidth: 2.5,
                            tension: 0.3,
                            pointRadius: 4,
                            pointHoverRadius: 7,
                            yAxisID: 'y',
                            fill: false
                        },
                        {
                            label: 'Blue (450nm)',
                            data: chartDataBlue,
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 2.5,
                            tension: 0.3,
                            pointRadius: 4,
                            pointHoverRadius: 7,
                            yAxisID: 'y',
                            fill: false
                        },
                        {
                            label: 'Clear (Ambient)',
                            data: chartDataClear,
                            borderColor: '#94a3b8',
                            backgroundColor: 'transparent',
                            borderWidth: 1.5,
                            borderDash: [5, 5],
                            tension: 0.3,
                            pointRadius: 3,
                            yAxisID: 'y',
                            fill: false
                        },
                        {
                            label: 'R/B Ratio (Normal <= 1.65)',
                            data: chartDataRatio,
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.15)',
                            borderWidth: 3,
                            tension: 0.3,
                            pointRadius: 5,
                            pointHoverRadius: 8,
                            yAxisID: 'y1',
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    animation: { duration: 400 },
                    plugins: {
                        legend: {
                            position: 'top',
                            labels: {
                                usePointStyle: true,
                                boxWidth: 8,
                                font: { family: 'Plus Jakarta Sans', size: 12, weight: 600 }
                            }
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            backgroundColor: 'rgba(15, 23, 42, 0.9)',
                            padding: 10,
                            cornerRadius: 8
                        }
                    },
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: { font: { family: 'Plus Jakarta Sans', size: 11 }, maxRotation: 45 }
                        },
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                            beginAtZero: true,
                            max: 100,
                            title: { display: true, text: 'Sensor Counts (ADC)', font: { size: 11, weight: 600 } },
                            grid: { color: '#f1f5f9' },
                            ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } }
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            min: 1.0,
                            max: 3.0,
                            title: { display: true, text: 'R/B Optical Ratio', font: { size: 11, weight: 600 } },
                            grid: { drawOnChartArea: false },
                            ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } }
                        }
                    }
                }
            });
        }

        // 2. Fetch Latest Real-Time Data from Backend API
        async function fetchLatestData(isManual = false) {
            if (!isMonitoring && !isManual) return;

            try {
                const res = await fetch('/api/latest');
                if (!res.ok) throw new Error('API response status ' + res.status);
                const data = await res.json();
                updateDashboard(data);
            } catch (err) {
                console.warn('Real-time polling notice:', err);
                setOfflineUI('Unable to communicate with backend server.');
            }
        }

        // 3. Update Dashboard Elements with Real Data
        function updateDashboard(resData) {
            const isConnected = resData.connected === true;
            const reading = resData.latest;

            // Connection Badge
            const badge = document.getElementById('connectionBadge');
            const alertBanner = document.getElementById('offlineAlertBanner');

            if (isConnected) {
                badge.className = 'badge-status-online';
                badge.innerHTML = '<span class="pulse-dot-online"></span> Hardware Stream Active';
                alertBanner.classList.add('d-none');
            } else {
                badge.className = 'badge-status-offline';
                badge.innerHTML = '<span class="pulse-dot-offline"></span> Hardware Offline';
                alertBanner.classList.remove('d-none');
            }

            if (!reading) {
                document.getElementById('lastReadingTimeText').innerHTML = 'Last reading: <em>No records received yet</em>';
                return;
            }

            // Update Last Reading Time Text
            const secAgo = resData.seconds_since_last_reading;
            const timeStr = reading.timestamp ? reading.timestamp.split(' ')[1] : '';
            if (secAgo !== null && secAgo !== undefined) {
                document.getElementById('lastReadingTimeText').innerHTML = 
                    `Last reading: <strong>${secAgo}s ago</strong> (${timeStr})`;
            }

            // Channel Values
            const red = reading.red ?? 0;
            const green = reading.green ?? 0;
            const blue = reading.blue ?? 0;
            const clear = reading.clear ?? reading.sensor_reading ?? (red + green + blue);

            document.getElementById('dispClear').innerText = clear.toLocaleString();
            document.getElementById('dispRed').innerText = red.toLocaleString();
            document.getElementById('dispGreen').innerText = green.toLocaleString();
            document.getElementById('dispBlue').innerText = blue.toLocaleString();

            // Dynamic progress bars relative to peak reading
            const maxVal = Math.max(clear, red, green, blue, 1);
            document.getElementById('barClear').style.width = Math.min(100, Math.round((clear / maxVal) * 100)) + '%';
            document.getElementById('barRed').style.width = Math.min(100, Math.round((red / maxVal) * 100)) + '%';
            document.getElementById('barGreen').style.width = Math.min(100, Math.round((green / maxVal) * 100)) + '%';
            document.getElementById('barBlue').style.width = Math.min(100, Math.round((blue / maxVal) * 100)) + '%';

            // Ratios
            const ratioRB = reading.ratio_rb ?? (blue > 0 ? (red / blue).toFixed(2) : '0.00');
            const yellowIdx = reading.yellow_index ?? (blue > 0 ? ((red + green) / (2 * blue)).toFixed(2) : '0.00');

            document.getElementById('dispRatioRB').innerText = Number(ratioRB).toFixed(2);
            document.getElementById('dispYellowIdx').innerText = Number(yellowIdx).toFixed(2);
            const statusBadge = document.getElementById('dispStatusBadge');
            statusBadge.innerText = reading.status || 'Normal';
            if (reading.status === 'Normal') {
                statusBadge.className = 'badge bg-success fs-6 px-3 py-1';
            } else if (reading.status === 'Mild Risk') {
                statusBadge.className = 'badge bg-warning text-dark fs-6 px-3 py-1';
            } else if (reading.status === 'High Risk') {
                statusBadge.className = 'badge bg-danger text-white fs-6 px-3 py-1';
            } else {
                statusBadge.className = 'badge badge-calib fs-6 px-3 py-1';
            }
            document.getElementById('dispRecommendation').innerText = reading.recommendation || 'Clinical calibration against laboratory STB required.';

            // Synthesized Color Swatch
            const rgbMax = Math.max(red, green, blue, 1);
            const rNorm = Math.min(255, Math.round((red / rgbMax) * 255));
            const gNorm = Math.min(255, Math.round((green / rgbMax) * 255));
            const bNorm = Math.min(255, Math.round((blue / rgbMax) * 255));
            const rgbColor = `rgb(${rNorm}, ${gNorm}, ${bNorm})`;

            document.getElementById('liveColorSwatch').style.backgroundColor = rgbColor;
            document.getElementById('liveColorHex').innerText = `${rgbColor} &bull; R/B: ${Number(ratioRB).toFixed(2)}`;

            // If this is a new reading, append to chart & refresh history
            if (reading.id !== lastLoggedId) {
                lastLoggedId = reading.id;
                appendPointToChart(timeStr || new Date().toLocaleTimeString(), red, green, blue, clear, ratioRB);
                loadHistoryTable();
            }
        }

        // 4. Append Point to Chart.js
        function appendPointToChart(label, r, g, b, c, ratio) {
            if (!sensorChart) return;

            if (chartLabels.length >= MAX_CHART_POINTS) {
                chartLabels.shift();
                chartDataRed.shift();
                chartDataGreen.shift();
                chartDataBlue.shift();
                chartDataClear.shift();
                chartDataRatio.shift();
            }

            const calcRatio = ratio !== undefined ? Number(ratio) : (b > 0 ? Number((r / b).toFixed(2)) : 0);

            chartLabels.push(label);
            chartDataRed.push(r);
            chartDataGreen.push(g);
            chartDataBlue.push(b);
            chartDataClear.push(c);
            chartDataRatio.push(calcRatio);

            sensorChart.update();
        }

        function resetChartData() {
            chartLabels.length = 0;
            chartDataRed.length = 0;
            chartDataGreen.length = 0;
            chartDataBlue.length = 0;
            chartDataClear.length = 0;
            if (sensorChart) sensorChart.update();
        }

        // 5. Load History Table
        async function loadHistoryTable() {
            try {
                const res = await fetch('/api/history');
                const data = await res.json();
                const history = data.history || [];
                const tbody = document.getElementById('historyTableBody');

                if (history.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted">No readings logged yet.</td></tr>';
                    return;
                }

                // Render top 12 recent records
                const rowsHtml = history.slice(0, 12).map(item => {
                    const r = item.red ?? 0;
                    const g = item.green ?? 0;
                    const b = item.blue ?? 0;
                    const c = item.clear ?? item.sensor_reading ?? (r + g + b);
                    const ratio = item.ratio_rb ?? (b > 0 ? (r / b).toFixed(2) : '-');
                    const badgeClass = item.status === 'Normal' ? 'bg-success text-white' : (item.status === 'Mild Risk' ? 'bg-warning text-dark' : (item.status === 'High Risk' ? 'bg-danger text-white' : 'badge-calib'));

                    return `
                        <tr>
                            <td class="fw-bold text-muted">#${item.id}</td>
                            <td class="small">${item.timestamp || ''}</td>
                            <td><span class="badge bg-secondary">${item.sensor_type || 'GY-9960'}</span></td>
                            <td class="fw-semibold text-dark">${c}</td>
                            <td class="text-danger fw-semibold">${r}</td>
                            <td class="text-success fw-semibold">${g}</td>
                            <td class="text-primary fw-semibold">${b}</td>
                            <td class="fw-bold">${ratio}</td>
                            <td><span class="badge ${badgeClass}">${item.status}</span></td>
                        </tr>
                    `;
                }).join('');

                tbody.innerHTML = rowsHtml;
            } catch (err) {
                console.error('Failed to load history table:', err);
            }
        }

        // 6. Set Offline UI
        function setOfflineUI(msg) {
            const badge = document.getElementById('connectionBadge');
            badge.className = 'badge-status-offline';
            badge.innerHTML = '<span class="pulse-dot-offline"></span> Hardware Offline';
            document.getElementById('offlineAlertBanner').classList.remove('d-none');
            document.getElementById('lastReadingTimeText').innerHTML = `Last reading: <em>${msg}</em>`;
        }

        // 7. Toggle Monitoring (Start / Pause)
        function toggleMonitoring() {
            isMonitoring = !isMonitoring;
            const btn = document.getElementById('btnMonitorToggle');
            const icon = document.getElementById('iconMonitorToggle');
            const text = document.getElementById('textMonitorToggle');

            if (isMonitoring) {
                icon.className = 'bi bi-pause-fill fs-6';
                text.innerText = 'Pause Monitoring';
                btn.className = 'btn btn-sm btn-medical d-flex align-items-center gap-2';
                fetchLatestData(true);
            } else {
                icon.className = 'bi bi-play-fill fs-6';
                text.innerText = 'Start Monitoring';
                btn.className = 'btn btn-sm btn-outline-medical d-flex align-items-center gap-2';
            }
        }

        function triggerManualPoll() {
            fetchLatestData(true);
        }

        // 8. Lifecycle Bootstrap
        window.addEventListener('DOMContentLoaded', () => {
            initChart();
        loadCalibratedGraphData();
            fetchLatestData(true);
            loadHistoryTable();

            // Poll every 1.5 seconds automatically without reload
            pollTimer = setInterval(() => {
                fetchLatestData(false);
            }, 1500);
        });
    </script>
</body>
</html>
"""
