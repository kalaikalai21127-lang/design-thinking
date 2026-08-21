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
    """Optical Sensor Jaundice Screening Record Model"""
    __tablename__ = 'screenings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    sensor_reading = db.Column(db.Integer, nullable=False)  # Range 0 - 255
    status = db.Column(db.String(50), nullable=False)        # 'Normal', 'Mild Risk', 'High Risk'
    confidence_score = db.Column(db.Float, nullable=False)   # Percentage e.g. 85.5
    recommendation = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'patient_name': self.patient.name if self.patient else 'Anonymous',
            'age': self.patient.age if self.patient else 0,
            'gender': self.patient.gender if self.patient else 'Unspecified',
            'sensor_reading': self.sensor_reading,
            'status': self.status,
            'confidence': round(self.confidence_score, 1),
            'confidence_score': round(self.confidence_score, 1),
            'recommendation': self.recommendation or '',
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else None
        }
