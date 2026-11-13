-- ============================================================================
-- Smart Jaundice Screening System Using Optical Sensor Readings
-- Database Schema (SQLite / MySQL Compatible)
-- ============================================================================

-- Table: patients
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL DEFAULT 'Anonymous Patient',
    age INTEGER DEFAULT 0,
    gender VARCHAR(20) DEFAULT 'Unspecified',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: screenings
CREATE TABLE IF NOT EXISTS screenings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    sensor_reading INTEGER DEFAULT 0,
    sensor_type VARCHAR(50) DEFAULT 'AS7262',
    ch_violet FLOAT DEFAULT NULL,
    ch_blue FLOAT DEFAULT NULL,
    ch_green FLOAT DEFAULT NULL,
    ch_yellow FLOAT DEFAULT NULL,
    ch_orange FLOAT DEFAULT NULL,
    ch_red FLOAT DEFAULT NULL,
    illumination_mode VARCHAR(20) DEFAULT 'OFF',
    timestamp_ms BIGINT DEFAULT 0,
    reading_1 FLOAT DEFAULT NULL,
    reading_2 FLOAT DEFAULT NULL,
    reading_3 FLOAT DEFAULT NULL,
    reading_4 FLOAT DEFAULT NULL,
    status VARCHAR(50) NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    recommendation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Sample Initial Data for Testing (AS7262 Six-Channel Spectral Readings)
INSERT INTO patients (name, age, gender) VALUES
('Neonatal Test Alpha', 0, 'Male'),
('Neonatal Test Beta', 0, 'Female'),
('Calibration Reference Patient', 0, 'Unspecified');

INSERT INTO screenings (patient_id, sensor_reading, sensor_type, ch_violet, ch_blue, ch_green, ch_yellow, ch_orange, ch_red, status, confidence_score, recommendation) VALUES
(1, 0, 'AS7262', 14.25, 22.80, 31.50, 27.40, 20.10, 15.30, 'Calibration Required', 0.0, 'Raw 6-channel spectral data logged. Clinical calibration against laboratory serum total bilirubin (STB) standard required before diagnostic assessment.'),
(2, 0, 'AS7262', 8.50, 18.20, 30.10, 28.90, 22.40, 16.80, 'Calibration Required', 0.0, 'Raw 6-channel spectral data logged. Bilirubin peak (450nm) attenuation observed. Requires clinical laboratory correlation.'),
(3, 185, 'Simulation', NULL, NULL, NULL, NULL, NULL, NULL, 'Normal', 94.5, 'Legacy simulated optical transmission reading (0-255).');

