import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Patient(db.Model):
    """Patient Demographic Record Model"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, default='Anonymous Patient')
    age = db.Column(db.Integer, nullable=True, default=0)
    gender = db.Column(db.String(20), nullable=True, default='Unspecified')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationship to screening records
    screenings = db.relationship('Screening', backref='patient', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }


class Screening(db.Model):
    """AS7262 Spectral Sensor & Optical Jaundice Screening Record Model"""
    __tablename__ = 'screenings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Sensor metadata & legacy compatibility field
    sensor_type = db.Column(db.String(50), nullable=True, default='AS7262')
    sensor_reading = db.Column(db.Integer, nullable=True, default=0)  # Legacy compatibility (0 - 255)

    # AS7262 Six Calibrated Spectral Channels (Counts / calibrated optical irradiance)
    ch_violet = db.Column(db.Float, nullable=True)  # 450 nm (Bilirubin peak absorption)
    ch_blue = db.Column(db.Float, nullable=True)    # 500 nm
    ch_green = db.Column(db.Float, nullable=True)   # 550 nm (Melanin/Hemoglobin reference)
    ch_yellow = db.Column(db.Float, nullable=True)  # 570 nm
    ch_orange = db.Column(db.Float, nullable=True)  # 600 nm
    ch_red = db.Column(db.Float, nullable=True)     # 650 nm (Skin reference baseline)

    status = db.Column(db.String(50), nullable=False)        # 'Calibration Required', 'Normal', 'Mild Risk', 'High Risk'
    confidence_score = db.Column(db.Float, nullable=True, default=0.0)   # Percentage or 0.0 for uncalibrated
    recommendation = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        channels_dict = {
            'violet': round(self.ch_violet, 2) if self.ch_violet is not None else None,
            'blue': round(self.ch_blue, 2) if self.ch_blue is not None else None,
            'green': round(self.ch_green, 2) if self.ch_green is not None else None,
            'yellow': round(self.ch_yellow, 2) if self.ch_yellow is not None else None,
            'orange': round(self.ch_orange, 2) if self.ch_orange is not None else None,
            'red': round(self.ch_red, 2) if self.ch_red is not None else None
        }
        r_val = self.ch_red if self.ch_red is not None else 0.0
        g_val = self.ch_green if self.ch_green is not None else 0.0
        b_val = self.ch_blue if self.ch_blue is not None else 0.0
        clear_val = self.sensor_reading if self.sensor_reading is not None else 0
        ratio_rb = round(r_val / max(0.001, b_val), 2) if b_val > 0 else 0.0
        yellow_idx = round((r_val + g_val) / (2.0 * max(0.001, b_val)), 2) if b_val > 0 else 0.0

        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else 'Anonymous',
            'age': self.patient.age if self.patient else 0,
            'gender': self.patient.gender if self.patient else 'Unspecified',
            'sensor_type': self.sensor_type or 'GY-9960',
            'sensor_reading': self.sensor_reading if self.sensor_reading is not None else 0,
            'reading': self.sensor_reading if self.sensor_reading is not None else 0,
            'sensor_value': self.sensor_reading if self.sensor_reading is not None else 0,
            'clear': clear_val,
            'ratio_rb': ratio_rb,
            'yellow_index': yellow_idx,
            'channels': channels_dict,
            'violet': channels_dict['violet'],
            'blue': channels_dict['blue'],
            'green': channels_dict['green'],
            'yellow': channels_dict['yellow'],
            'orange': channels_dict['orange'],
            'red': channels_dict['red'],
            'status': self.status,
            'confidence': round(self.confidence_score, 1) if self.confidence_score is not None else 0.0,
            'confidence_score': round(self.confidence_score, 1) if self.confidence_score is not None else 0.0,
            'recommendation': self.recommendation or '',
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }

