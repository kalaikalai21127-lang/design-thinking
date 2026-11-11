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

    # Calibrated GY-9960 / APDS-9960 Optical Baseline (Based on empirical sensor readings)
    # Reference Reading: Clear: 76, Red: 38, Green: 30, Blue: 25
    CALIBRATED_BASELINE_CLEAR = 76.0
    CALIBRATED_BASELINE_RED = 38.0
    CALIBRATED_BASELINE_GREEN = 30.0
    CALIBRATED_BASELINE_BLUE = 25.0
    CALIBRATED_BASELINE_RATIO_RB = 1.55         # 38 / 25 = 1.52 - 1.58
    CALIBRATED_BASELINE_YELLOW_INDEX = 1.38     # (38 + 30) / (2 * 25) = 1.36 - 1.40

    # Optical Jaundice Screening Thresholds (Bilirubin selective blue absorption at 450-480nm)
    THRESHOLD_RB_NORMAL_MAX = 1.65              # R/B <= 1.65: Normal baseline
    THRESHOLD_RB_MILD_MAX = 2.10                # 1.65 < R/B <= 2.10: Mild Risk (attenuated blue)
    # R/B > 2.10: High Risk (severe blue absorption)

    THRESHOLD_YI_NORMAL_MAX = 1.45              # Yellow Index <= 1.45: Normal baseline
    THRESHOLD_YI_MILD_MAX = 1.85                # 1.45 < Yellow Index <= 1.85: Mild Risk
    # Yellow Index > 1.85: High Risk

    # Calibration & Clinical Safety Policy
    CALIBRATION_REQUIRED_STATUS = 'Calibration Required'
    CALIBRATION_REQUIRED_RECOMMENDATION = (
        'Experimental prototype reading captured. Raw spectral data logged. '
        'Clinical calibration against laboratory serum total bilirubin (STB) reference standard '
        'is recommended before diagnostic risk assessment.'
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

