"""
================================================================================
Smart Jaundice Screening System - Machine Learning Model Training Script
================================================================================
Future AI Integration Workflow:
1. Collect optical sensor readings from web app simulations & ESP32 hardware.
2. Export dataset to CSV via GET /export-dataset or web interface button.
3. Label/verify dataset with clinical Serum Total Bilirubin (STB) blood results.
4. Train Machine Learning model (Random Forest / Logistic Regression classifier).
5. Save model binary (jaundice_sensor_model.pkl).
6. Replace rule-based threshold logic with trained ML prediction engine.
================================================================================
"""

import os
import pandas as pd
import numpy as np

try:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("[WARNING] scikit-learn or joblib not installed. Install via: pip install pandas scikit-learn joblib")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'dataset', 'jaundice_optical_dataset.csv')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'jaundice_sensor_model.pkl')

def train_sensor_ml_model():
    """
    Trains a Machine Learning Random Forest Classifier on collected optical sensor dataset.
    Features: sensor_reading, age, gender_encoded
    Target: predicted_status (Normal, Mild Risk, High Risk)
    """
    if not SKLEARN_AVAILABLE:
        print("[ERROR] Cannot train model. Please install scikit-learn: pip install scikit-learn joblib pandas")
        return

    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset file not found at {DATASET_PATH}. Run web app and export dataset first.")
        return

    print(f"[INFO] Loading optical sensor dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)

    if len(df) < 5:
        print("[WARNING] Dataset has too few samples for ML training. Collect more sensor readings first.")
        return

    # Preprocessing
    df['gender_code'] = df['gender'].map({'Male': 0, 'Female': 1, 'Child': 2, 'Unspecified': 0}).fillna(0)
    
    # Features & Target
    X = df[['sensor_reading', 'age', 'gender_code']]
    y = df['predicted_status']

    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("[INFO] Training Random Forest Classifier on Optical Sensor Readings...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluation
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) if len(y_test) > 0 else 1.0
    print(f"[SUCCESS] Model Training Accuracy: {accuracy * 100:.2f}%")

    # Save model binary
    joblib.dump(clf, MODEL_SAVE_PATH)
    print(f"[SUCCESS] Trained ML model saved to: {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_sensor_ml_model()
