import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

class Config:
    """Configurable Application Settings and Sensor Thresholds for Jaundice Screening"""
    BASE_DIR = BASE_DIR
    PROJECT_ROOT = PROJECT_ROOT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-jaundice-optical-sensor-key-2026')
    
    # SQLite Database Configuration (with seamless migration path to PostgreSQL or MySQL)
    _db_url = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'jaundice_screening.db')}")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AS7262 6-Channel Visible Spectral Sensor Configuration
    SENSOR_TYPE_DEFAULT = 'AS7262'
    SPECTRAL_CHANNELS = ['violet', 'blue', 'green', 'yellow', 'orange', 'red']
    SPECTRAL_WAVELENGTHS = {
        'violet': 450,  # FWHM 40nm - Primary bilirubin optical absorption region
        'blue': 500,    # FWHM 40nm - Secondary absorption / skin reference
        'green': 550,   # FWHM 40nm - Melanin / hemoglobin reference band
        'yellow': 570,  # FWHM 40nm - Background tissue reference
        'orange': 600,  # FWHM 40nm - Background tissue reference
        'red': 650      # FWHM 40nm - Low absorption skin baseline reference
    }

    # Calibration & Clinical Safety Policy:
    # This is an experimental neonatal jaundice screening prototype, NOT a clinically validated diagnostic device.
    # Uncalibrated spectral readings CANNOT diagnose jaundice or determine bilirubin concentration without
    # pairing with laboratory Serum Total Bilirubin (STB) blood measurements.
    CALIBRATION_REQUIRED_STATUS = 'Calibration Required'
    CALIBRATION_REQUIRED_RECOMMENDATION = (
        'Experimental prototype reading captured. Raw 6-channel spectral data logged. '
        'Clinical calibration against laboratory serum total bilirubin (STB) reference standard '
        'is required before diagnostic risk prediction can be performed. Uncalibrated data must not be used for diagnosis.'
    )

    # Legacy MVP Simulation Thresholds (0 - 255 optical intensity range)
    # NOTE: These thresholds apply ONLY to simulated legacy single-channel inputs (0-255).
    # They MUST NOT be reused as AS7262 spectral thresholds or treated as bilirubin concentrations!
    THRESHOLD_NORMAL_MIN = 100
    THRESHOLD_MILD_MIN = 70
    THRESHOLD_HIGH_MAX = 69

    # Legacy simulation confidence factors
    BASE_CONFIDENCE_NORMAL = 90.0
    BASE_CONFIDENCE_MILD = 82.0
    BASE_CONFIDENCE_HIGH = 92.0

    # Dataset Export Settings
    DATASET_EXPORT_DIR = os.path.join(PROJECT_ROOT, 'dataset')

