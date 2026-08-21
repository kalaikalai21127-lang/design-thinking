# Smart Jaundice Optical Sensor Dataset Collection

This directory stores historical optical sensor datasets collected from user screenings and ESP32 hardware nodes.

## CSV Dataset Schema

| Column Name | Type | Description |
|---|---|---|
| `patient_id` | Integer | Unique identifier for patient record |
| `age` | Integer | Patient age in years |
| `gender` | String | Patient gender (`Male`, `Female`, `Unspecified`) |
| `sensor_reading` | Integer | Transmittance / reflectance light value ($$0 - 255$$) |
| `predicted_status` | String | Classified risk level (`Normal`, `Mild Risk`, `High Risk`) |
| `timestamp` | String | Date and time of screening |

## Machine Learning Integration Workflow

1. **Collect Data**: Every simulated or ESP32 sensor reading is automatically logged into the SQLite database.
2. **Export Dataset**: Click the **Export Dataset** button on the web app or trigger `GET /export-dataset`.
3. **Medical Validation**: Lab-verified Serum Total Bilirubin (STB) blood readings can be correlated with sensor readings to refine class labels.
4. **Train ML Classifier**: Run `python ml/train_model.py` to train a supervised Random Forest / Logistic Regression classifier on the dataset.
5. **Deploy ML Model**: Update `ml/predict.py` to replace rule-based threshold logic with the trained `jaundice_sensor_model.pkl` binary.
