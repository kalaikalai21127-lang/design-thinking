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
    sensor_reading INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    confidence_score FLOAT NOT NULL,
    recommendation TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Sample Initial Data for Testing
INSERT INTO patients (name, age, gender) VALUES
('Patient Alpha', 28, 'Male'),
('Patient Beta', 45, 'Female'),
('Patient Gamma', 12, 'Child');

INSERT INTO screenings (patient_id, sensor_reading, status, confidence_score, recommendation) VALUES
(1, 185, 'Normal', 94.5, 'Optical sensor reading is within the healthy range.'),
(2, 85, 'Mild Risk', 82.0, 'Borderline optical reading. Monitor symptoms.'),
(3, 42, 'High Risk', 92.5, 'High risk detected. Consult a healthcare professional.');
