# AS7262 Multi-Spectral Jaundice Screening Dataset Collection

This directory stores optical spectral screening datasets collected from the web interface and physical ESP32 + AMS AS7262 hardware nodes.

## CSV Dataset Schema

| Column Name | Data Type | Description |
|---|---|---|
| `patient_id` | Integer | Unique identifier for patient / subject record |
| `age` | Integer | Subject age in days or hours |
| `gender` | String | Subject gender (`Male`, `Female`, `Unspecified`) |
| `sensor_type` | String | Sensor model (`AS7262` spectral sensor or legacy `Simulation`) |
| `violet_450nm` | Float | Calibrated optical irradiance at 450 nm (primary bilirubin absorption peak, $\mu\text{W/cm}^2$) |
| `blue_500nm` | Float | Calibrated optical irradiance at 500 nm (bilirubin absorption slope) |
| `green_550nm` | Float | Calibrated optical irradiance at 550 nm (hemoglobin / melanin reference band) |
| `yellow_570nm` | Float | Calibrated optical irradiance at 570 nm (cutaneous tissue background reference) |
| `orange_600nm` | Float | Calibrated optical irradiance at 600 nm (cutaneous tissue background reference) |
| `red_650nm` | Float | Calibrated optical irradiance at 650 nm (skin baseline reflectance) |
| `sensor_reading` | Integer | Backward compatibility field (0 for spectral scans, 0 - 255 for legacy simulation) |
| `predicted_status` | String | Screening status (`Calibration Required`, `Normal`, `Mild Risk`, `High Risk`) |
| `confidence_score` | Float | Percentage confidence score (0.0% for uncalibrated prototype readings) |
| `timestamp` | String | Date and time when the screening was logged (UTC) |

---

## Raw Counts vs. Calibrated Spectral Readings

The AMS AS7262 sensor provides two distinct data representations:
1. **Raw ADC Counts (0 - 65,535)**:
   - 16-bit uncalibrated internal analog-to-digital converter counts directly from each photodiode channel.
   - Accessed via `sensor.getViolet()`, `sensor.getBlue()`, etc.
   - Dependent on sensor gain, integration time, and unit variance.
2. **Calibrated Spectral Values ($\mu\text{W/cm}^2$)**:
   - Scientifically calibrated values calculated using the sensor's factory-trimmed calibration registers.
   - Accessed via `sensor.getCalibratedViolet()`, `sensor.getCalibratedBlue()`, etc.
   - Normalized optical power per unit area, allowing direct comparison across different boards.

---

## Clinical Calibration Prerequisites

This system is an **experimental screening prototype**, not a clinically validated medical device.
To train a machine learning model or transition from `Calibration Required` to diagnostic screening:
1. **Paired Reference Measurements**: Every spectral reading must be paired with gold-standard **Serum Total Bilirubin (STB)** in mg/dL obtained from venous or capillary blood tests analyzed in a certified clinical laboratory.
2. **Cohort Diversity**: Data must encompass diverse neonatal gestational ages (preterm vs. term), postnatal hours of life (Bhutani nomogram correlation), and varying skin pigmentation phototypes.
3. **Controlled Measurement Protocol**: Direct contact or fixed distance shield to minimize ambient optical noise.
