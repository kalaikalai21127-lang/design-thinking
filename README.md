# Low-Cost Neonatal Jaundice Screening Prototype (NodeMCU ESP8266 & GY-9960)

![System Architecture](https://img.shields.io/badge/System-Design_Thinking_Prototype-teal)
![Sensor](https://img.shields.io/badge/Sensor-GY--9960_|_APDS--9960_RGB-purple)
![Hardware](https://img.shields.io/badge/Microcontroller-NodeMCU_ESP8266-orange)
![OLED](https://img.shields.io/badge/Display-0.96"_SSD1306_I2C-lightblue)
![Web Server](https://img.shields.io/badge/Onboard_Dashboard-Port_80_HTTP-green)
![Backend](https://img.shields.io/badge/Backend-Flask_|_SQLite-blue)

## 📌 Project Overview
This project is an experimental **low-cost neonatal jaundice screening prototype** utilizing a **NodeMCU ESP8266 microcontroller**, a **GY-9960 (APDS-9960 compatible) optical colour sensor**, an **SSD1306 0.96" I²C OLED display**, and an **embedded Web Dashboard running on Port 80**.

### Photometric Principle of Jaundice Detection:
Bilirubin exhibits peak optical absorption in the **blue-violet spectrum (~450 - 480 nm)**. As cutaneous bilirubin levels rise:
- Reflected **Blue light** intensity is significantly attenuated due to absorption.
- **Red and Green light** are reflected normally by skin tissue.
- The **Yellow-to-Blue Optical Index** `(Red + Green) / (2 * Blue)` and **R/B Ratio** increase proportionally.

---

## ⚠️ Clinical Research & Calibration Disclaimer
> [!IMPORTANT]
> **This is an experimental engineering research prototype, NOT a clinically certified medical device.**
> - Uncalibrated raw optical color readings **cannot and do not diagnose neonatal jaundice**.
> - Bilirubin concentrations and clinical risk categories cannot be inferred without pairing spectral readings against gold-standard laboratory **Serum Total Bilirubin (STB)** blood test reference measurements.
> - The system explicitly reports status: `Calibration Required` until an empirically validated model trained on certified clinical reference data is loaded.

---

## 🔌 Hardware Connections (NodeMCU ESP8266)

| Peripheral Pin | NodeMCU Pin | GPIO | Wire Purpose | Electrical Notes |
|---|---|---|---|---|
| **GY-9960 SDA & OLED SDA** | **D2** | **GPIO 4** | Shared I²C Data | Pull-up to 3.3V included on breakout boards |
| **GY-9960 SCL & OLED SCL** | **D1** | **GPIO 5** | Shared I²C Clock | Standard NodeMCU I²C clock line (100 kHz) |
| **Push Button** | **D6** | **GPIO 12** | Scan Trigger | Connect to **GND** (configured with internal `INPUT_PULLUP`) |
| **Diagnostic LED** | **D5** | **GPIO 14** | Scan Indicator | Connect through a **220–330 Ω resistor** to GND |
| **Sensor VCC & OLED VCC** | **3.3V (3V3)** | **3.3V** | Power Supply | **Must be 3.3V**. Do NOT connect to 5V (VIN)! |
| **Common GND** | **GND** | **GND** | Ground | Connect all ground pins together |

- *GY-9960 / APDS-9960 I²C Address*: `0x39`
- *SSD1306 OLED I²C Address*: `0x3C`

---

## 🌐 On-Board Web Dashboard (Port 80)
The NodeMCU ESP8266 hosts its own embedded web server on **Port 80**:
1. When connected to your local Wi-Fi, the OLED and Serial Monitor display the NodeMCU IP (e.g., `http://192.168.1.150`).
2. Open that URL on any PC or phone browser on the same Wi-Fi network.
3. If no Wi-Fi router is available, the NodeMCU automatically starts an Access Point:
   - **SSID**: `Jaundice-Screener-AP` (Password: `12345678`)
   - **Dashboard URL**: `http://192.168.4.1/`
4. The dashboard provides:
   - Live color swatch synthesis matching what the sensor sees
   - Real-time Red, Green, Blue, and Clear count meters
   - Jaundice optical ratios (R/B and Yellow Index)
   - "Take Optical Scan Now" button to trigger readings remotely via AJAX

---

## 💻 Arduino IDE Setup & Upload Instructions

### 1. Arduino IDE Board Configuration
1. Open **Arduino IDE** (v2.x or v1.8.x).
2. Go to **Tools > Board > ESP8266 Boards > NodeMCU 1.0 (ESP-12E Module)**.
3. Select your serial port under **Tools > Port** (e.g., `COM3`, `COM4`, etc.).
4. Set **Upload Speed** to `115200` or `921600`.
5. Set **CPU Frequency** to `80 MHz` (or `160 MHz`).

### 2. Required Libraries
Install via the Arduino Library Manager (**Sketch > Include Library > Manage Libraries...**):
1. **Adafruit SSD1306** (by Adafruit)
2. **Adafruit GFX Library** (by Adafruit)
3. **ArduinoJson** (v6 or v7 by Benoît Blanchon)
*(ESP8266WiFi, ESP8266WebServer, and Wire are included in the ESP8266 Core)*

### 3. Firmware Location
Open [`hardware/esp8266_sensor_node/esp8266_sensor_node.ino`](file:///hardware/esp8266_sensor_node/esp8266_sensor_node.ino) in Arduino IDE.
Update the Wi-Fi placeholders:
```cpp
const char* ssid     = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
```

### 4. Upload & Serial Monitor
1. Click the **Upload** button in the Arduino IDE.
2. If the ESP32 gets stuck on `Connecting......._____`, press and hold the **BOOT** button on the ESP32 board until uploading starts.
3. Once upload completes, open **Tools > Serial Monitor** and set baud rate to **115200 baud**.

---

## 🖥️ Expected Serial Monitor Output

```text
=================================================================
 Neonatal Jaundice Screening Prototype - ESP32 & AS7262 Node    
=================================================================
[SETUP] Initializing I2C bus on SDA: GPIO 21, SCL: GPIO 22...
[I2C] Probing for AMS AS7262 spectral sensor at address 0x49...
[SUCCESS] AS7262 visible spectral sensor detected and initialized.
[HARDWARE] Onboard white illumination LED configured (12.5mA mode).

[WIFI] Connecting to network: MyHomeWiFi......
[WIFI SUCCESS] Connected to Wi-Fi!
[WIFI] ESP32 Assigned IP: 192.168.1.155
[WIFI] Target Backend URL: http://192.168.1.100:5000/api/predict
=================================================================
 Starting continuous spectral measurement loop...                
=================================================================

-----------------------------------------------------------------
[SCAN #1] Triggering AS7262 spectral acquisition...
=== Calibrated Spectral Irradiance (uW/cm^2) ===
  Violet (450 nm - Bilirubin Absorption Peak) : 14.25
  Blue   (500 nm - Bilirubin Absorption Slope): 22.80
  Green  (550 nm - Hb / Reference Band)       : 31.50
  Yellow (570 nm - Background Tissue Band)    : 27.40
  Orange (600 nm - Background Tissue Band)    : 20.10
  Red    (650 nm - Cutaneous Baseline)        : 15.30
=== Raw Sensor ADC Counts (0 - 65535) ===
  Raw: V=142 | B=228 | G=315 | Y=274 | O=201 | R=153
[SAFETY DISCLAIMER] Experimental prototype reading. Calibration against Serum Total Bilirubin required.
[HTTP] Transmitting spectral payload to Flask REST API...
[HTTP SUCCESS] Response Code: 201
[HTTP RESPONSE] {"calibration_status":"Calibration Required","channels":{"blue":22.8,"green":31.5,"orange":20.1,"red":15.3,"violet":14.25,"yellow":27.4},"confidence":0.0,"id":6,"is_calibrated":false,"status":"Calibration Required"...}
```

---

## 📡 REST API & Real-Time Telemetry Specification

### 1. `POST /api/predict` (Hardware Ingestion)
Transmits real-time GY-9960 sensor telemetry from NodeMCU ESP8266:
```json
{
  "device_id": "NodeMCU_ESP8266_GY9960_01",
  "sensor_type": "GY-9960",
  "name": "NodeMCU Optical Subject",
  "red": 380,
  "green": 406,
  "blue": 319,
  "clear": 1163,
  "ratio_rb": 1.19,
  "sensor_value": 1163
}
```

### 2. `GET /api/latest` (Dashboard Polling Engine)
Returns the most recent reading and device connectivity status (polled by the web dashboard every 1.5s):
```json
{
  "connected": true,
  "seconds_since_last_reading": 0.4,
  "message": "Hardware stream active",
  "latest": {
    "id": 20,
    "sensor_type": "GY-9960",
    "clear": 1163,
    "red": 380.0,
    "green": 406.0,
    "blue": 319.0,
    "ratio_rb": 1.19,
    "yellow_index": 1.23,
    "status": "Calibration Required",
    "timestamp": "2026-10-25 19:52:19"
  }
}
```

---

## 🔍 Troubleshooting Guide

### Issue 1: Sensor Not Detected / I²C Scan Finds Zero Devices
If Serial Monitor outputs `[CRITICAL ERROR] GY-9960 sensor communication failed!`:
1. **Power Check**: Verify the sensor VCC is connected to the NodeMCU **3.3V pin** (not 5V, not VIN).
2. **Pin Mapping**: Check that SDA is firmly wired to **D2 (GPIO 4)** and SCL to **D1 (GPIO 5)**.
3. **I²C Addresses**: GY-9960 is at `0x39`, and the SSD1306 OLED is at `0x3C`.
4. **Push Button**: Connected to **D6 (GPIO 12)** and **GND** (internal `INPUT_PULLUP`).
5. **LED**: Connected to **D5 (GPIO 14)** through a 220–330Ω resistor to GND.

### Issue 2: HTTP Connection Fails (`[HTTP BACKEND] Response Code: -1`)
1. **LAN IP Address**: Ensure `backendUrl` in the `.ino` sketch uses your computer's actual local IPv4 address (found via `ipconfig` in Command Prompt, e.g., `http://192.168.1.100:5000/api/predict`), **not** `localhost` or `127.0.0.1`.
2. **Firewall**: Windows Defender Firewall may block incoming connections on port 5000. Add an inbound rule allowing Python or port 5000 on private networks.
3. **Same Wi-Fi Network**: Ensure both your NodeMCU and your development PC are connected to the exact same Wi-Fi router / mobile hotspot subnet.
4. **Flask Host**: Ensure the Flask backend is running on `0.0.0.0:5000`.

---

## 🚀 Running and Testing the Dashboard

### 1. Start the Flask Backend Server
```bash
# In project root with active venv:
python backend/app.py
```
Open your browser at `http://127.0.0.1:5000` to view the Real-Time Optical Monitoring Dashboard.

### 2. Simulate Telemetry (If Hardware is Not Yet Powered)
```bash
python simulate_nodemcu_hardware.py --interval 1.5
```
Watch the live dashboard update every 1.5 seconds with live Clear, Red, Green, and Blue readings and rolling Chart.js line graph!

### 3. Flash Physical NodeMCU ESP8266
1. Open [`hardware/esp32_sensor_node.ino`](file:///hardware/esp32_sensor_node.ino) or [`hardware/esp8266_sensor_node/esp8266_sensor_node.ino`](file:///hardware/esp8266_sensor_node/esp8266_sensor_node.ino) in Arduino IDE.
2. Update `ssid`, `password`, and your PC's IP in `backendUrl`.
3. Select Board: **NodeMCU 1.0 (ESP-12E Module)**, Port: your COM port.
4. Upload firmware and watch real-time data stream directly onto the OLED and web dashboard!
