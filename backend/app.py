import os
import sys
import csv
import io
import sqlite3
from datetime import datetime

# Ensure backend directory is in sys.path before local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, Response, render_template_string
from flask_cors import CORS

from config import Config
from models import db, Patient, Screening

# Full Standalone Medical UI HTML Template with standard HTML 'class' attributes & modern medical CSS
# Real-time Hardware Monitoring Dashboard UI Template
from dashboard_template import DASHBOARD_HTML as UI_TEMPLATE


def _migrate_database_schema(db_path):
    """
    Seamlessly migrates the SQLite screenings table to add AS7262 spectral columns if not present.
    """
    if not os.path.exists(db_path):
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(screenings)")
        existing_cols = [row[1] for row in cursor.fetchall()]

        new_columns = [
            ("sensor_type", "VARCHAR(50) DEFAULT 'AS7262'"),
            ("ch_violet", "FLOAT DEFAULT NULL"),
            ("ch_blue", "FLOAT DEFAULT NULL"),
            ("ch_green", "FLOAT DEFAULT NULL"),
            ("ch_yellow", "FLOAT DEFAULT NULL"),
            ("ch_orange", "FLOAT DEFAULT NULL"),
            ("ch_red", "FLOAT DEFAULT NULL")
        ]

        for col_name, col_def in new_columns:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE screenings ADD COLUMN {col_name} {col_def}")
                print(f"[MIGRATION] Added column '{col_name}' to screenings table.")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[WARNING] Database schema migration error: {e}")

def create_app():
    """Flask Application Factory for AS7262 Neonatal Jaundice Spectral Screening System"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    db.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Auto-migrate SQLite schema if file exists
    db_file = os.path.join(Config.BASE_DIR, 'jaundice_screening.db')
    _migrate_database_schema(db_file)

    # Create Database Tables Automatically
    with app.app_context():
        db.create_all()
        _seed_initial_data()

    # Ensure dataset output directory exists
    os.makedirs(app.config['DATASET_EXPORT_DIR'], exist_ok=True)

    # ------------------------------------------------------------------------
    # Spectral & Simulation Prediction Logic
    # ------------------------------------------------------------------------
    def evaluate_spectral_reading(channels):
        """
        Evaluates AS7262 6-channel visible spectral data.
        In accordance with clinical safety principles, uncalibrated spectral readings
        CANNOT diagnose jaundice or compute a bilirubin concentration without empirical
        calibration against reference Serum Total Bilirubin (STB) blood tests.
        Returns: (status, confidence, recommendation)
        """
        status = Config.CALIBRATION_REQUIRED_STATUS
        confidence = 0.0
        recommendation = Config.CALIBRATION_REQUIRED_RECOMMENDATION
        return status, confidence, recommendation

    def evaluate_legacy_analog_reading(reading_val):
        """
        Legacy rule-based evaluation for simulated single-channel inputs (0 - 255).
        Returns: (status, confidence, recommendation)
        """
        normal_min = app.config['THRESHOLD_NORMAL_MIN']  # 100
        mild_min = app.config['THRESHOLD_MILD_MIN']      # 70

        if reading_val >= normal_min:
            status = "Normal"
            confidence = min(99.0, app.config['BASE_CONFIDENCE_NORMAL'] + ((reading_val - normal_min) / 155.0) * 8.0)
            recommendation = "Simulated optical transmission is within normal range."
        elif reading_val >= mild_min:
            status = "Mild Risk"
            confidence = min(95.0, app.config['BASE_CONFIDENCE_MILD'] + ((99 - reading_val) / 30.0) * 10.0)
            recommendation = "Simulated optical transmission is borderline. Re-test and monitor."
        else:
            status = "High Risk"
            confidence = min(98.0, app.config['BASE_CONFIDENCE_HIGH'] + ((69 - reading_val) / 69.0) * 6.0)
            recommendation = "Simulated optical transmission flagged high risk. Clinical follow-up recommended."

        return status, round(confidence, 1), recommendation

    # ------------------------------------------------------------------------
    # FRONTEND ROUTE - Renders Web App Interface
    # ------------------------------------------------------------------------

    @app.route('/', methods=['GET'])
    def home_ui():
        """Serves full interactive medical web application directly"""
        return render_template_string(UI_TEMPLATE)

    # ------------------------------------------------------------------------
    # REST API ENDPOINTS
    # ------------------------------------------------------------------------

    # 1. POST /predict or /api/predict
    @app.route('/predict', methods=['POST'])
    @app.route('/api/predict', methods=['POST'])
    def predict():
        data = request.get_json() or {}

        patient_name = str(data.get('name', 'Anonymous Subject')).strip() or 'Anonymous Subject'
        patient_age = data.get('age', 0)
        try:
            patient_age = int(patient_age) if patient_age is not None else 0
        except (ValueError, TypeError):
            patient_age = 0
        patient_gender = str(data.get('gender', 'Unspecified')).strip() or 'Unspecified'

        # Check for AS7262 spectral channel data (either nested or top-level)
        channels_input = data.get('channels')
        if not isinstance(channels_input, dict):
            # Check if top-level channel keys exist
            if all(k in data for k in ['violet', 'blue', 'green', 'yellow', 'orange', 'red']):
                channels_input = {k: data[k] for k in ['violet', 'blue', 'green', 'yellow', 'orange', 'red']}

        # Check for GY-9960 / APDS-9960 RGB channel data
        is_rgb_sensor = (data.get('sensor_type') in ['GY-9960', 'APDS-9960', 'GY9960', 'APDS9960']) or \
                         (all(k in data for k in ['red', 'green', 'blue']) and not channels_input)

        sensor_type = data.get('sensor_type', 'AS7262' if channels_input else ('GY-9960' if is_rgb_sensor else 'Simulation'))

        if channels_input:
            # --- AS7262 6-CHANNEL SPECTRAL PATH ---
            try:
                ch_violet = float(channels_input.get('violet', 0))
                ch_blue = float(channels_input.get('blue', 0))
                ch_green = float(channels_input.get('green', 0))
                ch_yellow = float(channels_input.get('yellow', 0))
                ch_orange = float(channels_input.get('orange', 0))
                ch_red = float(channels_input.get('red', 0))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid spectral channels. Values must be numeric numbers.'}), 400

            # Backward compatibility field: sensor_value can be optionally passed or defaulted to 0
            compat_sensor_value = data.get('sensor_value', 0)
            try:
                compat_sensor_value = int(compat_sensor_value)
            except (ValueError, TypeError):
                compat_sensor_value = 0

            status, confidence, recommendation = evaluate_spectral_reading({
                'violet': ch_violet, 'blue': ch_blue, 'green': ch_green,
                'yellow': ch_yellow, 'orange': ch_orange, 'red': ch_red
            })

            try:
                patient = Patient(name=patient_name, age=patient_age, gender=patient_gender)
                db.session.add(patient)
                db.session.flush()

                screening = Screening(
                    patient_id=patient.id,
                    sensor_type='AS7262',
                    sensor_reading=compat_sensor_value,
                    ch_violet=ch_violet,
                    ch_blue=ch_blue,
                    ch_green=ch_green,
                    ch_yellow=ch_yellow,
                    ch_orange=ch_orange,
                    ch_red=ch_red,
                    status=status,
                    confidence_score=confidence,
                    recommendation=recommendation
                )
                db.session.add(screening)
                db.session.commit()

                res_dict = screening.to_dict()
                res_dict['patient'] = patient.to_dict()
                res_dict['is_calibrated'] = False
                res_dict['calibration_status'] = 'Calibration Required'
                res_dict['disclaimer'] = 'Experimental prototype: uncalibrated spectral data cannot diagnose jaundice without laboratory STB reference.'
                return jsonify(res_dict), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Failed to record spectral screening: {str(e)}'}), 500

        elif is_rgb_sensor:
            # --- GY-9960 / APDS-9960 RGB COLOR SENSOR PATH (NodeMCU ESP8266) ---
            try:
                ch_red = float(data.get('red', 0))
                ch_green = float(data.get('green', 0))
                ch_blue = float(data.get('blue', 0))
                ch_violet = float(data.get('violet', ch_blue * 0.85)) # Optical absorption slope
                ch_yellow = float(data.get('yellow', (ch_red + ch_green) / 2.0))
                ch_orange = float(data.get('orange', (ch_red * 2.0 + ch_green) / 3.0))
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid RGB color channels. Values must be numeric numbers.'}), 400

            compat_sensor_value = data.get('clear', data.get('sensor_value', 0))
            try:
                compat_sensor_value = int(compat_sensor_value)
            except (ValueError, TypeError):
                compat_sensor_value = 0

            status = Config.CALIBRATION_REQUIRED_STATUS
            confidence = 0.0
            recommendation = 'GY-9960 optical RGB color data captured. Laboratory serum total bilirubin (STB) calibration required.'

            try:
                patient = Patient(name=patient_name, age=patient_age, gender=patient_gender)
                db.session.add(patient)
                db.session.flush()

                screening = Screening(
                    patient_id=patient.id,
                    sensor_type=sensor_type,
                    sensor_reading=compat_sensor_value,
                    ch_violet=ch_violet,
                    ch_blue=ch_blue,
                    ch_green=ch_green,
                    ch_yellow=ch_yellow,
                    ch_orange=ch_orange,
                    ch_red=ch_red,
                    status=status,
                    confidence_score=confidence,
                    recommendation=recommendation
                )
                db.session.add(screening)
                db.session.commit()

                res_dict = screening.to_dict()
                res_dict['patient'] = patient.to_dict()
                res_dict['is_calibrated'] = False
                res_dict['calibration_status'] = 'Calibration Required'
                res_dict['disclaimer'] = 'Experimental prototype: uncalibrated optical color data cannot diagnose jaundice without laboratory STB reference.'
                return jsonify(res_dict), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Failed to record GY-9960 screening: {str(e)}'}), 500

        else:
            # --- LEGACY SIMULATION / ANALOG SINGLE-CHANNEL PATH ---
            sensor_val_raw = data.get('sensor_value', data.get('reading', None))
            if sensor_val_raw is None:
                return jsonify({
                    'error': 'Missing required sensor data. Please provide AS7262 channels {"violet", "blue", "green", "yellow", "orange", "red"} or legacy "sensor_value".'
                }), 400

            try:
                sensor_value = int(sensor_val_raw)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid "sensor_value". Must be an integer between 0 and 255.'}), 400

            if not (0 <= sensor_value <= 255):
                return jsonify({'error': '"sensor_value" must be in the range 0 to 255.'}), 400

            status, confidence, recommendation = evaluate_legacy_analog_reading(sensor_value)

            try:
                patient = Patient(name=patient_name, age=patient_age, gender=patient_gender)
                db.session.add(patient)
                db.session.flush()

                screening = Screening(
                    patient_id=patient.id,
                    sensor_type='Simulation',
                    sensor_reading=sensor_value,
                    ch_violet=None,
                    ch_blue=None,
                    ch_green=None,
                    ch_yellow=None,
                    ch_orange=None,
                    ch_red=None,
                    status=status,
                    confidence_score=confidence,
                    recommendation=recommendation
                )
                db.session.add(screening)
                db.session.commit()

                res_dict = screening.to_dict()
                res_dict['patient'] = patient.to_dict()
                return jsonify(res_dict), 201

            except Exception as e:
                db.session.rollback()
                return jsonify({'error': f'Failed to record screening: {str(e)}'}), 500

    # 2. GET /history or /api/history
    @app.route('/history', methods=['GET'])
    @app.route('/api/history', methods=['GET'])
    def get_history():
        screenings = Screening.query.order_by(Screening.timestamp.desc()).all()
        return jsonify({
            'count': len(screenings),
            'history': [s.to_dict() for s in screenings]
        }), 200

    # 3. GET /statistics or /api/statistics
    @app.route('/statistics', methods=['GET'])
    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        all_screenings = Screening.query.all()
        total_screenings = len(all_screenings)

        calib_req_cases = sum(1 for s in all_screenings if s.status == 'Calibration Required')
        normal_cases = sum(1 for s in all_screenings if s.status == 'Normal')
        mild_cases = sum(1 for s in all_screenings if s.status == 'Mild Risk')
        high_cases = sum(1 for s in all_screenings if s.status == 'High Risk')

        recent_screenings = [s.to_dict() for s in all_screenings[-5:][::-1]]

        return jsonify({
            'total_screenings': total_screenings,
            'calibration_required_cases': calib_req_cases,
            'normal_cases': normal_cases,
            'mild_cases': mild_cases,
            'high_cases': high_cases,
            'recent_screenings': recent_screenings
        }), 200

    # 3b. GET /latest or /api/latest (Real-time Hardware Stream Endpoint)
    @app.route('/latest', methods=['GET'])
    @app.route('/api/latest', methods=['GET'])
    def get_latest():
        latest = Screening.query.order_by(Screening.id.desc()).first()
        if not latest:
            return jsonify({
                'connected': False,
                'seconds_since_last_reading': None,
                'latest': None,
                'message': 'No hardware sensor data received yet.'
            }), 200

        now = datetime.utcnow()
        seconds_ago = (now - latest.timestamp).total_seconds() if latest.timestamp else 999999.0
        # Device is considered active if a reading was logged within the last 15 seconds
        is_connected = (seconds_ago <= 15.0)

        return jsonify({
            'connected': is_connected,
            'seconds_since_last_reading': round(seconds_ago, 1),
            'latest': latest.to_dict(),
            'message': 'Hardware stream active' if is_connected else f'Device offline (last seen {int(seconds_ago)}s ago)'
        }), 200

    # 3c. GET /api/nodemcu/proxy (Direct bridge to NodeMCU Port 80)
    @app.route('/api/nodemcu/proxy', methods=['GET'])
    def proxy_nodemcu():
        ip = request.args.get('ip', '').strip()
        if not ip:
            return jsonify({'error': 'Missing NodeMCU IP address parameter'}), 400
        try:
            import urllib.request
            url = f"http://{ip}/api/data"
            req = urllib.request.Request(url, headers={'User-Agent': 'Flask-Dashboard-Bridge'})
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = resp.read().decode('utf-8')
                return Response(data, mimetype='application/json')
        except Exception as e:
            return jsonify({'error': f'Failed to reach NodeMCU at {ip}: {str(e)}'}), 502

    # 4. GET /export-dataset or /api/export-dataset
    @app.route('/export-dataset', methods=['GET'])
    @app.route('/api/export-dataset', methods=['GET'])
    def export_dataset():
        screenings = Screening.query.order_by(Screening.id.asc()).all()

        csv_filename = 'jaundice_optical_dataset.csv'
        csv_file_path = os.path.join(app.config['DATASET_EXPORT_DIR'], csv_filename)

        headers = [
            'patient_id', 'age', 'gender', 'sensor_type',
            'violet_450nm', 'blue_500nm', 'green_550nm', 'yellow_570nm', 'orange_600nm', 'red_650nm',
            'sensor_reading', 'predicted_status', 'confidence_score', 'timestamp'
        ]

        def get_row(s):
            return [
                s.patient_id,
                s.patient.age if s.patient else 0,
                s.patient.gender if s.patient else 'Unspecified',
                s.sensor_type or 'AS7262',
                s.ch_violet if s.ch_violet is not None else '',
                s.ch_blue if s.ch_blue is not None else '',
                s.ch_green if s.ch_green is not None else '',
                s.ch_yellow if s.ch_yellow is not None else '',
                s.ch_orange if s.ch_orange is not None else '',
                s.ch_red if s.ch_red is not None else '',
                s.sensor_reading if s.sensor_reading is not None else 0,
                s.status,
                s.confidence_score if s.confidence_score is not None else 0.0,
                s.timestamp.strftime('%Y-%m-%d %H:%M:%S') if s.timestamp else ''
            ]

        # Write to local dataset directory
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for s in screenings:
                writer.writerow(get_row(s))

        # Output to HTTP response buffer
        output_buffer = io.StringIO()
        writer = csv.writer(output_buffer)
        writer.writerow(headers)
        for s in screenings:
            writer.writerow(get_row(s))

        response = Response(output_buffer.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename={csv_filename}'
        return response

    # 5. DELETE /record/<id> or /api/record/<id>
    @app.route('/record/<int:record_id>', methods=['DELETE'])
    @app.route('/api/record/<int:record_id>', methods=['DELETE'])
    def delete_record(record_id):
        screening = Screening.query.get(record_id)
        if not screening:
            return jsonify({'error': f'Record #{record_id} not found.'}), 404

        try:
            patient_id = screening.patient_id
            db.session.delete(screening)
            
            if Screening.query.filter_by(patient_id=patient_id).count() == 1:
                patient = Patient.query.get(patient_id)
                if patient:
                    db.session.delete(patient)

            db.session.commit()
            return jsonify({'message': f'Screening record #{record_id} deleted successfully.'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Failed to delete record: {str(e)}'}), 500

    return app

def _seed_initial_data():
    """Seeds initial sample records including AS7262 spectral records"""
    if Screening.query.count() == 0:
        sample_patients = [
            Patient(name='Neonate Test Subject Alpha', age=0, gender='Male'),
            Patient(name='Neonate Test Subject Beta', age=0, gender='Female'),
            Patient(name='Calibration Reference Neonate', age=0, gender='Unspecified')
        ]
        db.session.add_all(sample_patients)
        db.session.flush()

        sample_screenings = [
            Screening(
                patient_id=sample_patients[0].id,
                sensor_type='AS7262',
                ch_violet=14.25, ch_blue=22.80, ch_green=31.50,
                ch_yellow=27.40, ch_orange=20.10, ch_red=15.30,
                sensor_reading=0,
                status='Calibration Required',
                confidence_score=0.0,
                recommendation='Raw 6-channel spectral data logged. Clinical calibration against laboratory serum total bilirubin (STB) standard required before diagnostic assessment.'
            ),
            Screening(
                patient_id=sample_patients[1].id,
                sensor_type='AS7262',
                ch_violet=8.50, ch_blue=18.20, ch_green=30.10,
                ch_yellow=28.90, ch_orange=22.40, ch_red=16.80,
                sensor_reading=0,
                status='Calibration Required',
                confidence_score=0.0,
                recommendation='Raw 6-channel spectral data logged. Attenuation at 450nm noted. Requires paired STB reference test for clinical calibration.'
            ),
            Screening(
                patient_id=sample_patients[2].id,
                sensor_type='Simulation',
                ch_violet=None, ch_blue=None, ch_green=None,
                ch_yellow=None, ch_orange=None, ch_red=None,
                sensor_reading=185,
                status='Normal',
                confidence_score=94.5,
                recommendation='Legacy optical simulation reading within normal range.'
            )
        ]
        db.session.add_all(sample_screenings)
        db.session.commit()
        print("[INFO] Seeded AS7262 spectral and legacy screening data.")

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[SUCCESS] Neonatal Jaundice AS7262 Spectral Screening API running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
