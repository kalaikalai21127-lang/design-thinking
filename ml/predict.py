"""
================================================================================
AS7262 Spectral Neonatal Jaundice Screening - Inference Predictor Module
================================================================================
This module provides an inference interface for the AS7262 multi-spectral sensor.
If a validated calibrated model binary exists, it generates calibrated predictions.
When no validated clinical model is loaded, it strictly reports 'Calibration Required',
preventing unverified diagnostic claims.
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

class SpectralJaundicePredictor:
    """AS7262 Multi-Spectral Model Inference Predictor"""
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        """Loads trained pkl model if available"""
        if JOBLIB_AVAILABLE and os.path.exists(MODEL_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                print(f"[INFO] Calibrated spectral ML model loaded from: {MODEL_PATH}")
            except Exception as e:
                print(f"[WARNING] Failed to load model from {MODEL_PATH}: {e}")
                self.model = None

    def predict_spectral(self, channels, age=0, gender='Unspecified'):
        """
        Runs ML prediction if a calibrated model exists.
        If uncalibrated, returns a structured status indicating 'Calibration Required'.
        """
        if self.model is None:
            # Uncalibrated prototype state
            return {
                'status': 'Calibration Required',
                'is_calibrated': False,
                'calibration_status': 'Calibration Required',
                'confidence': 0.0,
                'confidence_score': 0.0,
                'recommendation': (
                    'Raw 6-channel spectral measurements recorded. '
                    'Clinical calibration against laboratory Serum Total Bilirubin (STB) reference '
                    'is required before diagnostic risk predictions can be made. Experimental prototype only.'
                ),
                'disclaimer': 'Experimental prototype: uncalibrated spectral readings cannot diagnose neonatal jaundice.'
            }

        try:
            v = float(channels.get('violet', 0))
            b = float(channels.get('blue', 0))
            g = float(channels.get('green', 0))
            y = float(channels.get('yellow', 0))
            o = float(channels.get('orange', 0))
            r = float(channels.get('red', 0))

            input_df = pd.DataFrame([{
                'violet_450nm': v,
                'blue_500nm': b,
                'green_550nm': g,
                'yellow_570nm': y,
                'orange_600nm': o,
                'red_650nm': r,
                'ratio_violet_green': v / (g + 1e-6),
                'ratio_violet_red': v / (r + 1e-6),
                'ratio_blue_yellow': b / (y + 1e-6)
            }])

            prediction = self.model.predict(input_df)[0]
            confidence = 90.0
            if hasattr(self.model, 'predict_proba'):
                probs = self.model.predict_proba(input_df)[0]
                confidence = float(max(probs) * 100.0)

            recommendations = {
                'Normal': "Optical reading classified as Normal by calibrated model.",
                'Mild Risk': "Optical reading classified as Mild Risk. Follow clinical jaundice protocol.",
                'High Risk': "Optical reading classified as High Risk. Immediate serum bilirubin laboratory test recommended."
            }

            return {
                'status': prediction,
                'is_calibrated': True,
                'calibration_status': 'Calibrated',
                'confidence': round(confidence, 1),
                'confidence_score': round(confidence, 1),
                'recommendation': recommendations.get(prediction, 'Consult medical professional.')
            }

        except Exception as e:
            print(f"[ERROR] Inference error: {e}")
            return {
                'status': 'Calibration Required',
                'is_calibrated': False,
                'confidence': 0.0,
                'recommendation': f'Inference error: {str(e)}'
            }

    # Backward compatibility method for legacy single-value queries
    def predict(self, sensor_reading, age=0, gender='Unspecified'):
        return None  # Let backend use fallback logic

spectral_predictor = SpectralJaundicePredictor()
