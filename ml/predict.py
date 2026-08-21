"""
================================================================================
Smart Jaundice Screening System - Machine Learning Prediction Module
================================================================================
This script provides an inference interface for the trained ML model.
It can seamlessly replace rule-based threshold logic in backend/app.py.
================================================================================
"""

import os
import pandas as pd

try:
    import joblib
    JOBLIB_AVAILABLE = True
except ImportError:
    JOBLIB_AVAILABLE = False

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'jaundice_sensor_model.pkl')

class JaundiceMLPredictor:
    """ML Model Inference Predictor for Optical Sensor Readings"""
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads trained pkl model if available"""
        if JOBLIB_AVAILABLE and os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"[INFO] ML Model loaded successfully from {MODEL_PATH}")
            except Exception as e:
                print(f"[WARNING] Failed to load ML model: {e}")

    def predict(self, sensor_reading, age=0, gender='Unspecified'):
        """
        Runs ML prediction if model exists, otherwise returns None to fallback to rule-based logic.
        """
        if self.model is None:
            return None  # Fallback to rule-based thresholds

        gender_code = 0
        if gender == 'Female': gender_code = 1
        elif gender == 'Child': gender_code = 2

        input_df = pd.DataFrame([{
            'sensor_reading': sensor_reading,
            'age': age,
            'gender_code': gender_code
        }])

        try:
            prediction = self.model.predict(input_df)[0]
            probabilities = self.model.predict_proba(input_df)[0]
            confidence = float(max(probabilities) * 100.0)

            recommendations = {
                'Normal': "Optical reading classified as Normal by ML model.",
                'Mild Risk': "Optical reading classified as Mild Risk by ML model. Monitor patient.",
                'High Risk': "Optical reading classified as High Risk by ML model. Refer for blood bilirubin test."
            }

            return {
                'status': prediction,
                'confidence': round(confidence, 1),
                'recommendation': recommendations.get(prediction, 'Consult medical professional.')
            }
        except Exception as e:
            print(f"[ERROR] ML Prediction error: {e}")
            return None

ml_predictor = JaundiceMLPredictor()
