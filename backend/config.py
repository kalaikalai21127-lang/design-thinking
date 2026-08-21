import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))

class Config:
    """Configurable Application Settings and Sensor Thresholds for Jaundice Screening"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-jaundice-optical-sensor-key-2026')
    
    # SQLite Database Configuration (with seamless migration path to MySQL)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(BASE_DIR, 'jaundice_screening.db')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurable MVP Rule-Based Sensor Thresholds (0 - 255 optical intensity range)
    # 100 - 255: Normal Light Transmission
    # 70 - 99: Mild Risk
    # 0 - 69: High Risk
    THRESHOLD_NORMAL_MIN = 100
    THRESHOLD_MILD_MIN = 70
    THRESHOLD_HIGH_MAX = 69

    # Confidence calculation factors
    BASE_CONFIDENCE_NORMAL = 90.0
    BASE_CONFIDENCE_MILD = 82.0
    BASE_CONFIDENCE_HIGH = 92.0

    # Dataset Export Settings
    DATASET_EXPORT_DIR = os.path.join(PROJECT_ROOT, 'dataset')
