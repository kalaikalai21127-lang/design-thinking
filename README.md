# Smart Jaundice Screening System Using Optical Sensor Readings

![System Architecture](https://img.shields.io/badge/System-Design_Thinking-teal)
![Tech Stack](https://img.shields.io/badge/Stack-React_|_Flask_|_SQLite-blue)
![Hardware](https://img.shields.io/badge/Hardware-ESP32_|_TCS34725-orange)

## 📌 Project Vision & Overview
The **Smart Jaundice Screening System Using Optical Sensor Readings** is a full-stack medical screening platform developed for a Design Thinking initiative. The system uses optical sensor data to measure light transmittance through tissue/finger to assess jaundice risk.

In this platform:
1. Optical sensor readings ($$0 - 255$$) are simulated via a responsive medical web interface.
2. Every screening is stored in a structured database (SQLite / MySQL) to collect an AI dataset.
3. Configurable rule-based thresholds classify risk into **Normal**, **Mild Risk**, or **High Risk**.
4. The system is architected for future hardware connection (ESP32) and Machine Learning model transition.

---

## 🛠️ Tech Stack
- **Frontend**: React.js, Bootstrap 5, Lucide Icons, Plus Jakarta Sans font.
- **Backend**: Python Flask, REST API, Flask-SQLAlchemy, Flask-CORS.
- **Database**: SQLite (default for MVP; architecture allows seamless migration to MySQL).
- **Future Hardware**: ESP32 microcontroller, TCS34725/TCS3200 color sensor, LED light source.
- **Future AI / ML**: Dataset collection (CSV export), scikit-learn Random Forest model training.

---

## 📁 Directory Structure
```
design thinking project 1/
│
├── backend/
│   ├── app.py                 # Flask REST API server with /predict, /history, /statistics, /export-dataset
│   ├── config.py              # Configurable sensor risk thresholds & DB settings
│   ├── models.py              # SQLAlchemy database ORM models (Patient, Screening)
│   ├── schema.sql             # SQL script for database creation
│   └── requirements.txt       # Python backend dependencies
│
├── frontend/
│   ├── index.html             # Main HTML entry with Bootstrap 5
│   ├── vite.config.js         # Vite configuration with API proxy
│   ├── package.json           # Frontend React dependencies
│   └── src/
│       ├── main.jsx           # React DOM root
│       ├── App.jsx            # Application routing setup
│       ├── index.css          # Medical UI design system styling
│       ├── services/
│       │   └── api.js         # Axios API client wrapper
│       ├── components/
│       │   ├── Navbar.jsx     # Navigation bar with dataset export button
│       │   ├── Footer.jsx     # Medical prototype footer
│       │   ├── RiskGauge.jsx  # Visual progress bar (0-255 spectrum)
│       │   └── ResultCard.jsx # Screening result card with recommendation
│       └── pages/
│           ├── Home.jsx       # Project vision, description & workflow
│           ├── Screening.jsx  # Interactive sensor input (0-255) & patient form
│           ├── Dashboard.jsx  # Metrics (Total, Normal, Mild, High Risk) & charts
│           ├── History.jsx    # Table with search, view, & delete actions
│           └── HardwareMLGuide.jsx # ESP32 hardware & ML dataset guide
│
├── dataset/
│   ├── jaundice_optical_dataset.csv  # Auto-generated CSV training dataset
│   ├── sample_sensor_data.csv        # Sample dataset seed
│   └── README.md                     # Dataset schema documentation
│
├── ml/
│   ├── train_model.py         # Supervised ML model training script (Random Forest)
│   └── predict.py             # Inference module for trained ML model transition
│
├── hardware/
│   └── esp32_sensor_node.ino  # ESP32 C++ firmware sketch for optical sensor
│
└── README.md                  # Comprehensive setup & project documentation
```

---

## ⚙️ Prediction Thresholds (MVP Rule Engine)

Risk categories are evaluated using configurable thresholds defined in `backend/config.py`:

| Sensor Value Range ($$0 - 255$$) | Predicted Risk Status | Confidence Score | Clinical Recommendation |
|---|---|---|---|
| **100 – 255** | **Normal** | $$90\% - 99\%$$ | Optical reading within healthy limits. No evidence of jaundice detected. |
| **70 – 99** | **Mild Risk** | $$82\% - 95\%$$ | Borderline optical reading detected. Monitor symptoms and re-test in 24h. |
| **0 – 69** | **High Risk** | $$92\% - 98\%$$ | Please consult a healthcare professional for further evaluation and blood bilirubin test. |

---

## 📡 REST API Documentation

### 1. Execute Screening / Prediction
- **Endpoint**: `POST /api/predict`
- **Request Body**:
```json
{
  "sensor_value": 85,
  "name": "Patient A",
  "age": 21,
  "gender": "Male"
}
```
- **Response**:
```json
{
  "id": 1,
  "reading": 85,
  "sensor_value": 85,
  "status": "Mild Risk",
  "confidence": 82.0,
  "recommendation": "Borderline optical reading detected. Monitor symptoms and re-test in 24h.",
  "patient": {
    "id": 1,
    "name": "Patient A",
    "age": 21,
    "gender": "Male"
  },
  "timestamp": "2026-08-21 20:45:00"
}
```

### 2. Get Screening History
- **Endpoint**: `GET /api/history`
- **Response**: Returns list of all stored screening records.

### 3. Get Dashboard Statistics
- **Endpoint**: `GET /api/statistics`
- **Response**: Returns total screenings count, normal count, mild risk count, high risk count, and recent history.

### 4. Export AI Training Dataset
- **Endpoint**: `GET /api/export-dataset`
- **Response**: CSV File stream with header `patient_id,age,gender,sensor_reading,predicted_status,timestamp`.

### 5. Delete Record
- **Endpoint**: `DELETE /api/record/{id}`
- **Response**: Confirms record deletion from SQLite database.

---

## 🔬 Machine Learning Transition Guide

1. **Collect Data**: Every simulated screening or ESP32 hardware reading is saved to `jaundice_screening.db`.
2. **Export Dataset**: Click **Export Dataset (CSV)** in the navbar or call `GET /api/export-dataset`.
3. **Train Model**: Run the training script:
   ```bash
   python ml/train_model.py
   ```
4. **Deploy AI Model**: `ml/predict.py` loads `jaundice_sensor_model.pkl` and overrides rule-based thresholds with ML probability predictions.

---

## 🔌 Hardware Integration (ESP32 / TCS34725)

The hardware architecture follows:
$$\text{LED Light Source} \longrightarrow \text{Tissue / Finger} \longrightarrow \text{TCS34725 Sensor} \longrightarrow \text{ESP32 ADC} \longrightarrow \text{Flask API} \longrightarrow \text{Database}$$

1. Flash the ESP32 using Arduino IDE with the provided sketch in `hardware/esp32_sensor_node.ino`.
2. Configure Wi-Fi SSID/password and Flask server IP address (`http://<SERVER_IP>:5000/api/predict`).
3. ESP32 will read analog optical transmittance, normalize value to 0-255, and send HTTP POST requests automatically.

---

## 🚀 Setup Instructions

### Backend Setup (Python Flask)
```bash
# Navigate to project root
cd "design thinking project 1"

# Create and activate Python virtual environment
py -m venv backend/venv
backend\venv\Scripts\activate   # On Windows

# Install backend dependencies
pip install Flask Flask-CORS Flask-SQLAlchemy pandas scikit-learn joblib

# Start Flask Backend Server
python backend/app.py
```
*Server runs on `http://127.0.0.1:5000`.*

### Frontend Setup (React + Vite)
```bash
# Navigate to frontend folder
cd frontend

# Install Node dependencies (if node/npm installed)
npm install

# Start Vite React Development Server
npm run dev
```
*Frontend runs on `http://localhost:3000`.*
