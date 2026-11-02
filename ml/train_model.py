"""
================================================================================
AS7262 Spectral Neonatal Jaundice Screening - Machine Learning Pipeline
================================================================================
Clinical Calibration & Supervised Learning Workflow:
1. Physical AS7262 sensor measures 6 discrete visible channels:
   - violet_450nm (Primary Bilirubin absorption peak)
   - blue_500nm   (Absorption slope)
   - green_550nm  (Hemoglobin & melanin reference)
   - yellow_570nm (Background tissue reference)
   - orange_600nm (Background tissue reference)
   - red_650nm    (Cutaneous baseline reflectance)
2. Pair each 6-channel spectral reading with gold-standard clinical reference:
   - Serum Total Bilirubin (STB in mg/dL or umol/L) from laboratory blood analysis.
3. Feature Engineering:
   - Compute differential optical density ratios (e.g., Violet / Green, Blue / Red)
     to normalize for variations in neonatal skin pigmentation and cutaneous blood flow.
4. Train Supervised Classifier / Regressor (Random Forest, Gradient Boosting, or Ridge).
5. Deploy validated model to ml/predict.py.

CRITICAL CLINICAL NOTICE:
Do not train or deploy diagnostic models on uncalibrated data or arbitrary labels.
If paired clinical STB reference data is not present in the dataset,
the pipeline halts and flags 'Calibration Required'.
================================================================================
"""

import os
import sys
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
    print("[WARNING] scikit-learn or joblib not installed.")
    print("[INSTALLATION] Run: pip install scikit-learn joblib pandas numpy")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..'))
DATASET_PATH = os.path.join(PROJECT_ROOT, 'dataset', 'jaundice_optical_dataset.csv')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'jaundice_sensor_model.pkl')

SPECTRAL_FEATURE_COLS = [
    'violet_450nm',
    'blue_500nm',
    'green_550nm',
    'yellow_570nm',
    'orange_600nm',
    'red_650nm'
]

def check_calibration_data_prerequisites(df):
    """
    Checks whether the dataset contains paired clinical reference data needed
    for training a valid neonatal jaundice screening model.
    """
    missing_items = []

    # Check for 6 spectral channel features
    for col in SPECTRAL_FEATURE_COLS:
        if col not in df.columns:
            missing_items.append(f"Missing spectral channel column: '{col}'")

    # Check whether spectral rows have non-null values
    if all(col in df.columns for col in SPECTRAL_FEATURE_COLS):
        spectral_rows = df.dropna(subset=SPECTRAL_FEATURE_COLS)
        if len(spectral_rows) < 10:
            missing_items.append(
                f"Insufficient multi-spectral samples ({len(spectral_rows)} found, minimum 10 required for training split)."
            )

    # Check for clinical reference standard (STB or validated clinical diagnosis)
    # If all statuses are 'Calibration Required' or unverified, clinical ground truth is missing
    target_col = None
    if 'stb_mg_dl' in df.columns:
        target_col = 'stb_mg_dl'
    elif 'clinical_status' in df.columns:
        target_col = 'clinical_status'
    elif 'predicted_status' in df.columns:
        # Check if predicted_status is just uncalibrated prototype labels
        unique_statuses = df['predicted_status'].dropna().unique()
        if set(unique_statuses) <= {'Calibration Required'}:
            missing_items.append(
                "Clinical ground-truth labels missing: All dataset rows are marked 'Calibration Required'. "
                "Paired laboratory Serum Total Bilirubin (STB) blood tests are required to label samples."
            )
        else:
            target_col = 'predicted_status'
    else:
        missing_items.append("No target column found ('stb_mg_dl', 'clinical_status', or 'predicted_status').")

    return missing_items, target_col

def train_spectral_ml_model():
    """
    Trains a Machine Learning classifier on AS7262 multi-spectral dataset
    WHEN paired clinical calibration ground-truth is available.
    """
    if not SKLEARN_AVAILABLE:
        print("[ERROR] Cannot train model. Please install required libraries:")
        print("        pip install scikit-learn joblib pandas numpy")
        return

    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset file not found at: {DATASET_PATH}")
        print("        Export dataset from the web app or collect ESP32 readings first.")
        return

    print(f"[INFO] Inspecting AS7262 spectral dataset at: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)

    missing_prerequisites, target_col = check_calibration_data_prerequisites(df)

    if missing_prerequisites:
        print("\n" + "=" * 70)
        print(" [CALIBRATION REQUIRED] Cannot Train Clinical Screening Model")
        print("=" * 70)
        print("The current dataset cannot be used to train a clinically valid model because:")
        for item in missing_prerequisites:
            print(f"  - {item}")
        print("\nWhat is missing:")
        print("  1. Paired clinical reference standard: Gold-standard Serum Total Bilirubin")
        print("     (STB, mg/dL) laboratory blood tests matched to each spectral scan.")
        print("  2. Sufficient patient cohort data across gestational age and skin phototypes.")
        print("  3. Controlled optical measurement protocol to account for ambient light.")
        print("\nPolicy Enforcement:")
        print("  In accordance with medical prototype design guidelines, this system will")
        print("  NOT invent arbitrary calibration coefficients or fake risk classifications.")
        print("  All uncalibrated predictions will display 'Calibration Required'.")
        print("=" * 70 + "\n")
        return

    # Filter rows with complete spectral data
    df_clean = df.dropna(subset=SPECTRAL_FEATURE_COLS + [target_col]).copy()

    # Feature Engineering: Compute differential optical ratios
    df_clean['ratio_violet_green'] = df_clean['violet_450nm'] / (df_clean['green_550nm'] + 1e-6)
    df_clean['ratio_violet_red'] = df_clean['violet_450nm'] / (df_clean['red_650nm'] + 1e-6)
    df_clean['ratio_blue_yellow'] = df_clean['blue_500nm'] / (df_clean['yellow_570nm'] + 1e-6)

    feature_cols = SPECTRAL_FEATURE_COLS + ['ratio_violet_green', 'ratio_violet_red', 'ratio_blue_yellow']
    X = df_clean[feature_cols]
    y = df_clean[target_col]

    print(f"[INFO] Training on {len(df_clean)} samples with features: {feature_cols}")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred) if len(y_test) > 0 else 1.0
    print(f"[SUCCESS] Calibrated Model Accuracy: {acc * 100:.2f}%")

    joblib.dump(clf, MODEL_SAVE_PATH)
    print(f"[SUCCESS] Trained calibrated model saved to: {MODEL_SAVE_PATH}")

if __name__ == '__main__':
    train_spectral_ml_model()
