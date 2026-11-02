/*
================================================================================
Low-Cost Neonatal Jaundice Screening Prototype
NodeMCU ESP8266 (ESP-12E) Firmware Sketch
================================================================================
Hardware Specifications:
- Microcontroller : NodeMCU ESP8266 (ESP-12E Module)
- Colour Sensor   : GY-9960 / APDS-9960-compatible RGB & Ambient Light Module (I2C 0x39)
- OLED Display    : 0.96-inch SSD1306 Monochrome 128x64 OLED (I2C 0x3C)
- Push Button     : NodeMCU D6 (GPIO 12) -> Connected to GND (using INPUT_PULLUP)
- Diagnostic LED  : NodeMCU D5 (GPIO 14) -> Connected to LED via 220-330 ohm resistor
- Power Supply    : 3.3V (3V3) & GND shared across NodeMCU, GY-9960, and SSD1306

Pin Mapping (NodeMCU ESP8266):
- I2C SDA         : D2 (GPIO 4) -> Connected to GY-9960 SDA and SSD1306 SDA
- I2C SCL         : D1 (GPIO 5) -> Connected to GY-9960 SCL and SSD1306 SCL
- Push Button     : D6 (GPIO 12) -> Pulls to GND on press (Triggers optical scan)
- Status LED      : D5 (GPIO 14) -> Active HIGH (with 220-330 ohm resistor to GND)
- VCC             : NodeMCU 3.3V (Do NOT use 5V for sensor or OLED)
- GND             : NodeMCU Common Ground (GND)

Features:
1. Native I2C driver for GY-9960 / APDS-9960 color sensor (0x39) - no extra sensor
   library installation required. Reads Red, Green, Blue, Clear channels.
2. SSD1306 0.96" OLED display (0x3C) showing live status, IP address, and R/G/B/C metrics.
3. Embedded Responsive Web Dashboard hosted directly on NodeMCU port 80 using ESP8266WebServer.
   Access via http://<ESP8266_IP>/ on any browser or smartphone.
4. Push button on D6 triggers immediate optical measurement, updates OLED, and updates web UI.
5. LED on D5 indicates scanning, Wi-Fi status, and diagnostic feedback.
6. Configurable Wi-Fi credentials with automatic fallback to SoftAP (192.168.4.1) if router is unavailable.
7. Optional background HTTP POST to Flask REST backend (/api/predict) for long-term database logging.
================================================================================
Required Arduino IDE Libraries:
1. "Adafruit SSD1306" (by Adafruit - install via Library Manager)
2. "Adafruit GFX Library" (by Adafruit - install via Library Manager)
3. "ArduinoJson" (v6 or v7 by Benoit Blanchon - install via Library Manager)
4. "ESP8266WiFi" & "ESP8266WebServer" & "Wire" (Built into ESP8266 Arduino Core)
================================================================================
*/

#include <Wire.h>
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================================
// HARDWARE PIN DEFINITIONS (NodeMCU ESP-12E)
// ============================================================================
#ifndef D1
  #define D1 5
#endif
#ifndef D2
  #define D2 4
#endif
#ifndef D5
  #define D5 14
#endif
#ifndef D6
  #define D6 12
#endif

// Official project pin assignments
const uint8_t PIN_I2C_SDA = D2; // GPIO 4  - Shared I2C Data (GY-9960 + SSD1306)
const uint8_t PIN_I2C_SCL = D1; // GPIO 5  - Shared I2C Clock (GY-9960 + SSD1306)
const uint8_t PIN_BUTTON  = D6; // GPIO 12 - Push Button to GND (INPUT_PULLUP)
const uint8_t PIN_LED     = D5; // GPIO 14 - Status / Illumination LED (Active HIGH)

// ============================================================================
// OLED DISPLAY DEFINITIONS (0.96" SSD1306 I2C 0x3C)
// ============================================================================
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1 // Shared reset
#define OLED_I2C_ADDR 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
bool oledDetected = false;

// ============================================================================
// GY-9960 / APDS-9960 I2C REGISTERS & DEFINITIONS (I2C Address: 0x39)
// ============================================================================
#define APDS9960_I2C_ADDR     0x39
#define APDS9960_REG_ENABLE   0x80
#define APDS9960_REG_ATIME    0x81
#define APDS9960_REG_WTIME    0x83
#define APDS9960_REG_CONTROL  0x8F
#define APDS9960_REG_ID       0x92
#define APDS9960_REG_STATUS   0x93
#define APDS9960_REG_CDATAL   0x94
#define APDS9960_PON          0x01 // Power ON
#define APDS9960_AEN          0x02 // ALS (Color) Enable
#define APDS9960_AVALID       0x01 // ALS Valid bit in STATUS

bool sensorDetected = false;

// ============================================================================
// WI-FI & WEB SERVER CONFIGURATION
// ============================================================================
// Configurable network credentials placeholder
// Replace with your local Wi-Fi router or mobile hotspot credentials
const char* ssid     = "nonetwork";
const char* password = "12345678";

// Fallback SoftAP credentials if router Wi-Fi is unavailable
const char* ap_ssid  = "Jaundice-Screener-AP";
const char* ap_pass  = "12345678";

// Embedded Web Server on Port 80
ESP8266WebServer server(80);

// Real-Time Automatic Background Streaming Configuration
// Set to true to automatically stream sensor readings to the Flask website every 1.5s
const bool ENABLE_BACKEND_UPLOAD = true;
const bool ENABLE_CONTINUOUS_STREAM = true;
const unsigned long STREAM_INTERVAL_MS = 1500; // Continuous stream every 1.5 seconds
unsigned long lastStreamTime = 0;

// IMPORTANT: Replace with your development PC's LAN IP address (run 'ipconfig' in command prompt)
const char* backendUrl = "http://10.248.212.98:5000/api/predict";

// ============================================================================
// OPTICAL READING DATA STRUCTURE
// ============================================================================
struct ColorReading {
  uint16_t red   = 0;
  uint16_t green = 0;
  uint16_t blue  = 0;
  uint16_t clear = 0;
  float ratioRB  = 0.0f; // Red to Blue ratio (indicates blue absorption)
  float yellowIndex = 0.0f; // (Red + Green) / (2 * Blue)
  String status = "Calibration Required";
  String recommendation = "Clinical calibration against serum total bilirubin (STB) required.";
  unsigned long readingIndex = 0;
  unsigned long timestampMs = 0;
  bool valid = false;
} lastReading;

unsigned long scanCounter = 0;
unsigned long lastBtnPressTime = 0;
const unsigned long DEBOUNCE_DELAY_MS = 250;

// ============================================================================
// LED CONTROL HELPERS
// ============================================================================
void ledOn()  { digitalWrite(PIN_LED, HIGH); }
void ledOff() { digitalWrite(PIN_LED, LOW); }

void ledBlink(int count, int onMs, int offMs) {
  for (int i = 0; i < count; i++) {
    digitalWrite(PIN_LED, HIGH);
    delay(onMs);
    digitalWrite(PIN_LED, LOW);
    if (i < count - 1) delay(offMs);
  }
}

// ============================================================================
// GY-9960 / APDS-9960 NATIVE I2C SENSOR DRIVER
// ============================================================================
bool initGY9960() {
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  if (Wire.endTransmission() != 0) {
    return false;
  }

  // Read Chip ID (0x92)
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_ID);
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)APDS9960_I2C_ADDR, (uint8_t)1);
  uint8_t chipId = Wire.available() ? Wire.read() : 0;
  Serial.printf("[GY-9960] Sensor identified at 0x39 (ID: 0x%02X)\n", chipId);

  // Power OFF first to reset state
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_ENABLE);
  Wire.write(0x00);
  Wire.endTransmission();
  delay(10);

  // Integration Time: ATIME = 0xD5 (~120ms integration time, optimal resolution)
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_ATIME);
  Wire.write(0xD5);
  Wire.endTransmission();

  // Control: Set ALS Gain = 4x (0x01)
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_CONTROL);
  Wire.write(0x01);
  Wire.endTransmission();

  // Enable: Power ON (PON) + Color ALS Enable (AEN) = 0x03
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_ENABLE);
  Wire.write(APDS9960_PON | APDS9960_AEN);
  Wire.endTransmission();

  delay(150); // Wait for first integration cycle
  return true;
}

bool readGY9960Color(uint16_t &r, uint16_t &g, uint16_t &b, uint16_t &c) {
  // Wait up to 250ms for AVALID bit in STATUS register (0x93)
  unsigned long startWait = millis();
  bool dataReady = false;
  while (millis() - startWait < 250) {
    Wire.beginTransmission(APDS9960_I2C_ADDR);
    Wire.write(APDS9960_REG_STATUS);
    Wire.endTransmission(false);
    Wire.requestFrom((uint8_t)APDS9960_I2C_ADDR, (uint8_t)1);
    if (Wire.available()) {
      uint8_t status = Wire.read();
      if (status & APDS9960_AVALID) {
        dataReady = true;
        break;
      }
    }
    delay(10);
  }

  // Request 8 bytes starting from CDATAL (0x94)
  Wire.beginTransmission(APDS9960_I2C_ADDR);
  Wire.write(APDS9960_REG_CDATAL);
  if (Wire.endTransmission(false) != 0) return false;

  if (Wire.requestFrom((uint8_t)APDS9960_I2C_ADDR, (uint8_t)8) == 8) {
    c = Wire.read() | (Wire.read() << 8);
    r = Wire.read() | (Wire.read() << 8);
    g = Wire.read() | (Wire.read() << 8);
    b = Wire.read() | (Wire.read() << 8);
    return true;
  }
  return false;
}

// Perform Optical Acquisition & Calculate Ratios
bool acquireSensorData(ColorReading &out) {
  if (!sensorDetected) {
    if (!initGY9960()) {
      Serial.println(F("[ERROR] GY-9960 not responding at 0x39!"));
      return false;
    }
    sensorDetected = true;
  }

  // Turn on diagnostic LED on D5 during measurement
  ledOn();
  delay(120); // Optical stabilization delay

  uint16_t r = 0, g = 0, b = 0, c = 0;
  bool ok = readGY9960Color(r, g, b, c);
  ledOff();

  if (!ok) {
    Serial.println(F("[ERROR] Failed to read color data from GY-9960!"));
    return false;
  }

  out.red   = r;
  out.green = g;
  out.blue  = b;
  out.clear = c;

  // Jaundice optical ratio calculation:
  // Bilirubin absorbs blue light (450-490nm). Elevated bilirubin lowers blue reflectance,
  // causing the Red/Blue ratio and (R+G)/(2*B) ratio to increase.
  float blueDiv = (b > 0) ? (float)b : 1.0f;
  out.ratioRB = (float)r / blueDiv;
  out.yellowIndex = ((float)r + (float)g) / (2.0f * blueDiv);

  // Safety protocol: Prototype status is 'Calibration Required'
  out.status = "Calibration Required";
  out.recommendation = "Optical color data captured. Laboratory serum total bilirubin (STB) calibration required.";
  out.readingIndex = ++scanCounter;
  out.timestampMs = millis();
  out.valid = true;

  // Serial Diagnostics
  Serial.println(F("-----------------------------------------------------------------"));
  Serial.printf("[SCAN #%lu] GY-9960 Optical Data (I2C 0x39):\n", out.readingIndex);
  Serial.printf("  Red   (620-700nm): %5u counts\n", r);
  Serial.printf("  Green (500-560nm): %5u counts\n", g);
  Serial.printf("  Blue  (440-490nm): %5u counts  <-- Bilirubin absorption slope\n", b);
  Serial.printf("  Clear (Ambient)  : %5u counts\n", c);
  Serial.printf("  R/B Optical Ratio: %5.2f\n", out.ratioRB);
  Serial.printf("  Yellow-Blue Index: %5.2f\n", out.yellowIndex);
  Serial.printf("  Status           : %s\n", out.status.c_str());
  Serial.println(F("-----------------------------------------------------------------"));

  return true;
}

// ============================================================================
// SSD1306 OLED DISPLAY FUNCTIONS
// ============================================================================
void oledPrintHeader(const char* title) {
  if (!oledDetected) return;
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE); // Inverted title bar
  display.setCursor(0, 0);
  display.print(F(" "));
  display.print(title);
  for (int i = strlen(title); i < 20; i++) display.print(F(" "));
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 11);
}

void oledShowBootStatus(const char* msg) {
  if (!oledDetected) return;
  oledPrintHeader("JAUNDICE SCREENER");
  display.setCursor(0, 16);
  display.println(F("NodeMCU ESP8266"));
  display.println(F("Sensor : GY-9960 (0x39)"));
  display.println(F("OLED   : SSD1306 (0x3C)"));
  display.println(F("---------------------"));
  display.setCursor(0, 48);
  display.println(msg);
  display.display();
}

void oledShowReadyScreen() {
  if (!oledDetected) return;
  oledPrintHeader("JAUNDICE SCREENER");
  display.setCursor(0, 13);
  
  if (WiFi.status() == WL_CONNECTED) {
    display.printf("IP: %s\n", WiFi.localIP().toString().c_str());
    display.println(F("Web: Port 80 (Ready)"));
  } else {
    display.printf("AP: %s\n", WiFi.softAPIP().toString().c_str());
    display.println(F("Web: http://192.168.4.1"));
  }
  
  display.printf("GY-9960: %s\n", sensorDetected ? "Ready (0x39)" : "NOT FOUND");
  display.println(F("---------------------"));
  display.println(F("Press D6: Take Scan"));
  display.display();
}

void oledShowScanning() {
  if (!oledDetected) return;
  oledPrintHeader("SAMPLING TISSUE");
  display.setCursor(0, 18);
  display.println(F("Optical LED Active..."));
  display.println(F("Reading R, G, B, C"));
  display.setCursor(0, 42);
  display.println(F("Hold sensor steady"));
  display.drawRect(0, 56, 128, 6, SSD1306_WHITE);
  display.fillRect(2, 58, 64, 2, SSD1306_WHITE);
  display.display();
}

void oledShowResults(const ColorReading &r) {
  if (!oledDetected) return;
  display.clearDisplay();

  // Header with scan ID
  display.setTextSize(1);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setCursor(0, 0);
  display.printf(" SCAN #%lu | PORT 80   ", r.readingIndex);
  display.setTextColor(SSD1306_WHITE);

  // Status banner
  display.setCursor(0, 11);
  display.print(F("Status: "));
  display.println(r.status);

  // 4 Color channels: R, G, B, C
  display.setCursor(0, 23);
  display.printf("R:%4u   G:%4u\n", r.red, r.green);
  display.printf("B:%4u   C:%4u\n", r.blue, r.clear);

  // Optical metrics
  display.setCursor(0, 43);
  display.printf("R/B Ratio  : %4.2f\n", r.ratioRB);
  display.printf("Yellow-Idx : %4.2f\n", r.yellowIndex);

  // Footer prompt
  display.setCursor(0, 56);
  display.print(F("D6: Scan | Web UI live"));
  display.display();
}

void oledShowError(const char* title, const char* desc) {
  if (!oledDetected) return;
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print(F(" HARDWARE ERROR      "));
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 14);
  display.println(title);
  display.println(F("---------------------"));
  display.println(desc);
  display.display();
}

// ============================================================================
// EMBEDDED WEB DASHBOARD HTML (HOSTED DIRECTLY ON NODEMCU PORT 80)
// ============================================================================
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neonatal Jaundice Screening - NodeMCU ESP8266 & GY-9960</title>
    <style>
        :root {
            --primary: #0d9488;
            --primary-dark: #0f766e;
            --accent: #0284c7;
            --dark: #0f172a;
            --slate: #475569;
            --light-bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --warning-bg: #fffbeb;
            --warning-border: #fde68a;
            --warning-text: #b45309;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: var(--light-bg);
            color: var(--dark);
            padding: 16px;
            min-height: 100vh;
        }
        .container { max-width: 900px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            padding: 24px;
            border-radius: 16px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(13, 148, 136, 0.3);
        }
        .header h1 { font-size: 1.6rem; font-weight: 800; margin-bottom: 6px; }
        .header p { opacity: 0.9; font-size: 0.95rem; }
        .badges { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
        .badge {
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.04);
        }
        .card h2 { font-size: 1.15rem; font-weight: 700; color: var(--dark); margin-bottom: 14px; }
        .alert-warning {
            background: var(--warning-bg);
            border: 1px solid var(--warning-border);
            color: var(--warning-text);
            padding: 14px;
            border-radius: 12px;
            font-size: 0.85rem;
            line-height: 1.4;
            margin-bottom: 20px;
        }
        .grid-4 { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 12px; margin-bottom: 16px; }
        .channel-box {
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            background: #fafafa;
        }
        .channel-box .label { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; margin-bottom: 4px; }
        .channel-box .value { font-size: 1.4rem; font-weight: 800; }
        .chip-red   { color: #dc2626; border-top: 4px solid #dc2626; }
        .chip-green { color: #16a34a; border-top: 4px solid #16a34a; }
        .chip-blue  { color: #2563eb; border-top: 4px solid #2563eb; }
        .chip-clear { color: #64748b; border-top: 4px solid #64748b; }
        .metrics-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 16px; }
        .metric-card {
            background: #f1f5f9;
            border-radius: 12px;
            padding: 14px;
        }
        .metric-card .title { font-size: 0.8rem; color: var(--slate); font-weight: 600; }
        .metric-card .num { font-size: 1.5rem; font-weight: 800; color: var(--dark); margin-top: 4px; }
        .color-preview-box {
            display: flex;
            align-items: center;
            gap: 16px;
            background: #f8fafc;
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 12px 16px;
            margin-bottom: 16px;
        }
        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 10px;
            border: 2px solid white;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            background: #ffffff;
            flex-shrink: 0;
        }
        .btn {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.3);
            transition: all 0.2s;
        }
        .btn:hover { opacity: 0.95; transform: translateY(-1px); }
        .btn:active { transform: translateY(0); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .actions-bar { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-bottom: 20px; }
        .table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        .table th, .table td { padding: 10px; border-bottom: 1px solid var(--border); text-align: left; }
        .table th { background: #f8fafc; color: var(--slate); font-weight: 600; }
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 700;
            background: #fef3c7;
            color: #92400e;
        }
        .footer { text-align: center; color: var(--slate); font-size: 0.8rem; margin-top: 24px; padding-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>Neonatal Jaundice Screening Prototype</h1>
            <p>NodeMCU ESP8266 & GY-9960 / APDS-9960 Optical Colour Sensor Node</p>
            <div class="badges">
                <span class="badge">Board: NodeMCU ESP8266</span>
                <span class="badge">Sensor: GY-9960 (I2C 0x39)</span>
                <span class="badge">OLED: SSD1306 (I2C 0x3C)</span>
                <span class="badge">Port: 80 (HTTP)</span>
            </div>
        </div>

        <!-- Clinical Safety Alert -->
        <div class="alert-warning">
            <strong>Clinical Research Notice:</strong> This device is an experimental engineering research prototype, NOT a certified medical diagnostic device. Raw transcutaneous optical measurements require empirical calibration against laboratory Serum Total Bilirubin (STB) blood tests before clinical risk evaluation.
        </div>

        <!-- Actions -->
        <div class="actions-bar">
            <button id="scanBtn" class="btn" onclick="triggerScan()">Take Optical Scan Now</button>
            <label style="font-size: 0.85rem; color: var(--slate); display: flex; align-items: center; gap: 6px; cursor: pointer;">
                <input type="checkbox" id="autoRefresh" checked onchange="toggleAutoRefresh(this.checked)"> Auto-refresh live data (2s)
            </label>
            <span id="scanStatus" style="font-size: 0.85rem; font-weight: 600; color: var(--primary);"></span>
        </div>

        <!-- Real-Time Sensor Telemetry Card -->
        <div class="card">
            <h2>Real-Time Optical Telemetry (GY-9960)</h2>

            <!-- Synthesized Color Swatch -->
            <div class="color-preview-box">
                <div id="colorSwatch" class="color-swatch"></div>
                <div>
                    <div style="font-weight: 700; font-size: 0.95rem;">Live Optical Sample Synthesis</div>
                    <div id="swatchLabel" style="font-size: 0.8rem; color: var(--slate);">Synthesized from Red, Green, Blue sensor counts</div>
                </div>
            </div>

            <!-- 4 Channels Grid -->
            <div class="grid-4">
                <div class="channel-box chip-red">
                    <div class="label">Red (650nm)</div>
                    <div class="value" id="valRed">0</div>
                </div>
                <div class="channel-box chip-green">
                    <div class="label">Green (550nm)</div>
                    <div class="value" id="valGreen">0</div>
                </div>
                <div class="channel-box chip-blue">
                    <div class="label">Blue (450nm)</div>
                    <div class="value" id="valBlue">0</div>
                </div>
                <div class="channel-box chip-clear">
                    <div class="label">Clear (Lux)</div>
                    <div class="value" id="valClear">0</div>
                </div>
            </div>

            <!-- Metrics -->
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="title">Optical Status</div>
                    <div class="num" style="font-size: 1.15rem; color: #b45309;">
                        <span id="valStatus" class="status-badge">Calibration Required</span>
                    </div>
                </div>
                <div class="metric-card">
                    <div class="title">Red / Blue Ratio (R/B)</div>
                    <div class="num" id="valRatioRB">0.00</div>
                </div>
                <div class="metric-card">
                    <div class="title">Yellow-to-Blue Index</div>
                    <div class="num" id="valYellowIdx">0.00</div>
                </div>
                <div class="metric-card">
                    <div class="title">Total Scans Logged</div>
                    <div class="num" id="valScans">0</div>
                </div>
            </div>
        </div>

        <!-- Hardware Pinout & Diagnostics Card -->
        <div class="card">
            <h2>Hardware Wiring & NodeMCU Pinout</h2>
            <table class="table">
                <thead>
                    <tr><th>Peripheral Pin</th><th>NodeMCU ESP8266 Pin</th><th>GPIO</th><th>Electrical Function</th></tr>
                </thead>
                <tbody>
                    <tr><td><strong>GY-9960 SDA & OLED SDA</strong></td><td><strong>D2</strong></td><td>GPIO 4</td><td>Shared I2C Serial Data (Address 0x39 & 0x3C)</td></tr>
                    <tr><td><strong>GY-9960 SCL & OLED SCL</strong></td><td><strong>D1</strong></td><td>GPIO 5</td><td>Shared I2C Serial Clock (100 kHz)</td></tr>
                    <tr><td><strong>Push Button</strong></td><td><strong>D6</strong></td><td>GPIO 12</td><td>Triggers optical scan (INPUT_PULLUP to GND)</td></tr>
                    <tr><td><strong>Status / Illumination LED</strong></td><td><strong>D5</strong></td><td>GPIO 14</td><td>Active HIGH indicator (via 220-330 ohm resistor)</td></tr>
                    <tr><td><strong>VCC / Power</strong></td><td><strong>3.3V (3V3)</strong></td><td>3.3V</td><td>Power rail (3.3V regulated)</td></tr>
                    <tr><td><strong>GND</strong></td><td><strong>GND</strong></td><td>GND</td><td>Common system ground</td></tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            Design Thinking Low-Cost Jaundice Screening System &bull; NodeMCU ESP8266 HTTP Server Port 80 &bull; Bilirubin Spectral Optical Research
        </div>
    </div>

    <script>
        let refreshTimer = null;

        async function fetchSensorData() {
            try {
                const res = await fetch('/api/data');
                if (!res.ok) return;
                const data = await res.json();
                updateUI(data);
            } catch (err) {
                console.log('Telemetry fetch error:', err);
            }
        }

        function updateUI(data) {
            document.getElementById('valRed').innerText = data.red ?? 0;
            document.getElementById('valGreen').innerText = data.green ?? 0;
            document.getElementById('valBlue').innerText = data.blue ?? 0;
            document.getElementById('valClear').innerText = data.clear ?? 0;
            document.getElementById('valRatioRB').innerText = (data.ratio_rb ?? 0).toFixed(2);
            document.getElementById('valYellowIdx').innerText = (data.yellow_index ?? 0).toFixed(2);
            document.getElementById('valScans').innerText = data.reading_count ?? 0;
            document.getElementById('valStatus').innerText = data.status || 'Calibration Required';

            // Calculate synthesized RGB preview
            const r = data.red || 0, g = data.green || 0, b = data.blue || 0;
            const maxVal = Math.max(r, g, b, 1);
            const rNorm = Math.min(255, Math.round((r / maxVal) * 255));
            const gNorm = Math.min(255, Math.round((g / maxVal) * 255));
            const bNorm = Math.min(255, Math.round((b / maxVal) * 255));
            document.getElementById('colorSwatch').style.backgroundColor = `rgb(${rNorm}, ${gNorm}, ${bNorm})`;
            document.getElementById('swatchLabel').innerText = `RGB Color: rgb(${rNorm}, ${gNorm}, ${bNorm}) | R/B: ${(data.ratio_rb || 0).toFixed(2)}`;
        }

        async function triggerScan() {
            const btn = document.getElementById('scanBtn');
            const status = document.getElementById('scanStatus');
            btn.disabled = true;
            status.innerText = 'Scanning sensor...';
            try {
                const res = await fetch('/api/scan');
                const data = await res.json();
                updateUI(data);
                status.innerText = 'Scan completed!';
                setTimeout(() => { status.innerText = ''; }, 3000);
            } catch (err) {
                status.innerText = 'Scan failed: ' + err;
            } finally {
                btn.disabled = false;
            }
        }

        function toggleAutoRefresh(enable) {
            if (enable) {
                if (!refreshTimer) refreshTimer = setInterval(fetchSensorData, 2000);
            } else {
                if (refreshTimer) { clearInterval(refreshTimer); refreshTimer = null; }
            }
        }

        // Initialize on load
        fetchSensorData();
        toggleAutoRefresh(true);
    </script>
</body>
</html>
)rawliteral";

// ============================================================================
// WEB SERVER ROUTE HANDLERS (PORT 80)
// ============================================================================
void handleRoot() {
  server.send_P(200, "text/html", INDEX_HTML);
}

void handleApiData() {
  #if defined(ARDUINOJSON_VERSION_MAJOR) && ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
  #else
    StaticJsonDocument<512> doc;
  #endif

  doc["device"]          = "NodeMCU-ESP8266-GY9960";
  doc["sensor"]          = "GY-9960";
  doc["sensor_address"]  = "0x39";
  doc["oled_address"]    = "0x3C";
  doc["red"]             = lastReading.red;
  doc["green"]           = lastReading.green;
  doc["blue"]            = lastReading.blue;
  doc["clear"]           = lastReading.clear;
  doc["ratio_rb"]        = lastReading.ratioRB;
  doc["yellow_index"]    = lastReading.yellowIndex;
  doc["status"]          = lastReading.status;
  doc["recommendation"]  = lastReading.recommendation;
  doc["reading_count"]   = lastReading.readingIndex;
  doc["timestamp_ms"]    = lastReading.timestampMs;
  doc["uptime_sec"]      = millis() / 1000;
  doc["ip"]              = (WiFi.status() == WL_CONNECTED) ? WiFi.localIP().toString() : WiFi.softAPIP().toString();
  doc["rssi"]            = (WiFi.status() == WL_CONNECTED) ? WiFi.RSSI() : 0;

  String jsonOut;
  serializeJson(doc, jsonOut);
  server.send(200, "application/json", jsonOut);
}

void handleApiScan() {
  oledShowScanning();
  ColorReading r;
  bool ok = acquireSensorData(r);
  if (ok) {
    lastReading = r;
    oledShowResults(r);
    ledBlink(2, 80, 80);
  } else {
    oledShowError("SCAN FAILED", "Check GY-9960 wiring\nSDA:D2, SCL:D1, 3.3V");
    ledBlink(4, 80, 80);
  }
  handleApiData();
}

void handleApiStatus() {
  #if defined(ARDUINOJSON_VERSION_MAJOR) && ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
  #else
    StaticJsonDocument<384> doc;
  #endif

  doc["board"]           = "NodeMCU ESP8266";
  doc["sensor_detected"] = sensorDetected;
  doc["oled_detected"]   = oledDetected;
  doc["pin_sda"]         = PIN_I2C_SDA; // D2 (GPIO 4)
  doc["pin_scl"]         = PIN_I2C_SCL; // D1 (GPIO 5)
  doc["pin_button"]      = PIN_BUTTON;  // D6 (GPIO 12)
  doc["pin_led"]         = PIN_LED;     // D5 (GPIO 14)
  doc["wifi_connected"]  = (WiFi.status() == WL_CONNECTED);
  doc["free_heap"]       = ESP.getFreeHeap();

  String jsonOut;
  serializeJson(doc, jsonOut);
  server.send(200, "application/json", jsonOut);
}

void handleNotFound() {
  server.send(404, "text/plain", "404 Not Found - NodeMCU Jaundice Screener");
}

// ============================================================================
// OPTIONAL FORWARDING TO FLASK REST BACKEND
// ============================================================================
void sendPayloadToFlaskBackend(const ColorReading &r) {
  if (!ENABLE_BACKEND_UPLOAD || WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  bool isHttps = String(backendUrl).startsWith("https://");

  #if defined(ARDUINOJSON_VERSION_MAJOR) && ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
  #else
    StaticJsonDocument<512> doc;
  #endif

  doc["device_id"]   = "NodeMCU_ESP8266_GY9960_01";
  doc["sensor_type"] = "GY-9960";
  doc["name"]        = "NodeMCU Optical Subject";
  doc["red"]         = r.red;
  doc["green"]       = r.green;
  doc["blue"]        = r.blue;
  doc["clear"]       = r.clear;
  doc["ratio_rb"]    = r.ratioRB;
  doc["sensor_value"]= 0;

  String payload;
  serializeJson(doc, payload);

  if (isHttps) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure(); // Allows connecting to hosted HTTPS endpoints without custom certs
    if (!http.begin(secureClient, backendUrl)) return;
    http.setTimeout(5000);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(payload);
    Serial.printf("[HTTP BACKEND (HTTPS)] Response Code: %d\n", httpCode);
    http.end();
  } else {
    WiFiClient client;
    if (!http.begin(client, backendUrl)) return;
    http.setTimeout(4000);
    http.addHeader("Content-Type", "application/json");
    int httpCode = http.POST(payload);
    Serial.printf("[HTTP BACKEND (HTTP)] Response Code: %d\n", httpCode);
    http.end();
  }
}

// ============================================================================
// ACTION: TRIGGER MEASUREMENT FROM PHYSICAL BUTTON (D6)
// ============================================================================
void triggerPhysicalButtonScan() {
  Serial.println(F("\n[BUTTON D6 PRESSED] Initiating Optical Measurement..."));
  oledShowScanning();

  ColorReading r;
  if (acquireSensorData(r)) {
    lastReading = r;
    oledShowResults(r);
    ledBlink(2, 100, 100);

    // Optional background forward to Flask API
    sendPayloadToFlaskBackend(r);
  } else {
    oledShowError("GY-9960 READ ERROR", "Verify I2C wiring:\nD2(SDA) D1(SCL) 3.3V");
    ledBlink(4, 100, 100);
  }
}

// ============================================================================
// WI-FI SETUP & FALLBACK SOFT-AP
// ============================================================================
void setupWiFi() {
  Serial.println();
  Serial.printf("[WIFI] Connecting to SSID: '%s'...\n", ssid);
  oledShowBootStatus("Connecting Wi-Fi...");

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  int attempts = 0;
  // Try connecting for ~10 seconds
  while (WiFi.status() != WL_CONNECTED && attempts < 25) {
    delay(400);
    digitalWrite(PIN_LED, !digitalRead(PIN_LED)); // Toggle LED while waiting
    Serial.print(F("."));
    attempts++;
  }
  digitalWrite(PIN_LED, LOW);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println(F("[WIFI SUCCESS] Connected to local network!"));
    Serial.printf("  - NodeMCU IP Address : %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  - Web Dashboard Port : 80 (http://%s/)\n", WiFi.localIP().toString().c_str());
    ledBlink(1, 400, 100);
  } else {
    Serial.println();
    Serial.println(F("[WIFI NOTICE] Could not connect to Wi-Fi. Launching SoftAP mode..."));
    WiFi.mode(WIFI_AP);
    WiFi.softAP(ap_ssid, ap_pass);
    IPAddress apIP = WiFi.softAPIP();
    Serial.printf("  - SoftAP SSID        : %s\n", ap_ssid);
    Serial.printf("  - SoftAP IP Address  : %s\n", apIP.toString().c_str());
    Serial.printf("  - Web Dashboard Port : 80 (http://%s/)\n", apIP.toString().c_str());
    ledBlink(3, 100, 100);
  }
}

// ============================================================================
// ARDUINO SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(500);

  // Initialize GPIO Pins
  pinMode(PIN_LED, OUTPUT);
  digitalWrite(PIN_LED, LOW);

  // Push button with internal pull-up (connected to GND)
  pinMode(PIN_BUTTON, INPUT_PULLUP);

  Serial.println();
  Serial.println(F("================================================================="));
  Serial.println(F(" Neonatal Jaundice Screening - NodeMCU ESP8266 & GY-9960 Node    "));
  Serial.println(F("================================================================="));
  Serial.printf("  - Microcontroller : NodeMCU ESP8266 (ESP-12E)\n");
  Serial.printf("  - I2C Bus Pins    : SDA=D2 (GPIO %d), SCL=D1 (GPIO %d)\n", PIN_I2C_SDA, PIN_I2C_SCL);
  Serial.printf("  - Push Button Pin : D6 (GPIO %d) [INPUT_PULLUP to GND]\n", PIN_BUTTON);
  Serial.printf("  - Diagnostic LED  : D5 (GPIO %d) [Active HIGH via resistor]\n", PIN_LED);
  Serial.printf("  - GY-9960 Sensor  : Address 0x39 (Color RGB + Clear)\n");
  Serial.printf("  - SSD1306 OLED    : Address 0x3C (128x64 Monochrome)\n");
  Serial.printf("  - Web Server      : Port 80 (ESP8266WebServer)\n");
  Serial.println(F("================================================================="));

  // Initialize I2C Bus on ESP8266 (SDA=D2, SCL=D1)
  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  Wire.setClock(100000); // 100 kHz standard I2C clock

  // Initialize SSD1306 OLED Display (Address 0x3C)
  Serial.println(F("[OLED] Initializing SSD1306 OLED at 0x3C..."));
  if (display.begin(SSD1306_SWITCHCAPVCC, OLED_I2C_ADDR)) {
    oledDetected = true;
    display.clearDisplay();
    display.display();
    Serial.println(F("[SUCCESS] SSD1306 OLED initialized."));
    oledShowBootStatus("Initializing sensors...");
  } else {
    oledDetected = false;
    Serial.println(F("[WARNING] SSD1306 OLED display not detected at 0x3C."));
  }

  // Initialize GY-9960 / APDS-9960 Color Sensor (Address 0x39)
  Serial.println(F("[GY-9960] Probing GY-9960 / APDS-9960 sensor at 0x39..."));
  if (initGY9960()) {
    sensorDetected = true;
    Serial.println(F("[SUCCESS] GY-9960 colour sensor initialized and ready!"));
  } else {
    sensorDetected = false;
    Serial.println(F("[CRITICAL ERROR] GY-9960 not detected at 0x39!"));
    Serial.println(F("  Check: VIN to 3.3V, GND, SDA to D2, SCL to D1."));
    if (oledDetected) {
      oledShowError("GY-9960 NOT FOUND", "Check I2C wiring:\nD2(SDA) D1(SCL) 3.3V");
    }
  }

  // Connect to Wi-Fi or launch SoftAP
  setupWiFi();

  // Configure Web Server Routes on Port 80
  server.on("/", HTTP_GET, handleRoot);
  server.on("/api/data", HTTP_GET, handleApiData);
  server.on("/api/scan", HTTP_GET, handleApiScan);
  server.on("/api/scan", HTTP_POST, handleApiScan);
  server.on("/api/status", HTTP_GET, handleApiStatus);
  server.onNotFound(handleNotFound);

  server.begin();
  Serial.println(F("[HTTP SERVER] ESP8266WebServer listening on port 80."));

  // Take initial baseline measurement
  if (sensorDetected) {
    ColorReading r;
    if (acquireSensorData(r)) {
      lastReading = r;
    }
  }

  // Display Ready Screen on OLED
  oledShowReadyScreen();

  Serial.println(F("================================================================="));
  Serial.println(F(" System ready! Press Push Button (D6) or access Web Dashboard    "));
  Serial.println(F(" to perform optical jaundice screening measurements.            "));
  Serial.println(F("=================================================================\n"));
}

// ============================================================================
// ARDUINO MAIN LOOP
// ============================================================================
void loop() {
  // Service incoming HTTP requests on Port 80 (NodeMCU embedded server)
  server.handleClient();

  // Allow ESP8266 Wi-Fi background stack to process
  yield();

  // Automatic real-time telemetry streaming to Flask backend (every 1.5 seconds)
  if (ENABLE_CONTINUOUS_STREAM && ENABLE_BACKEND_UPLOAD && (WiFi.status() == WL_CONNECTED)) {
    unsigned long now = millis();
    if (now - lastStreamTime >= STREAM_INTERVAL_MS) {
      lastStreamTime = now;
      ColorReading r;
      if (acquireSensorData(r)) {
        lastReading = r;
        oledShowResults(r);
        sendPayloadToFlaskBackend(r);
      }
    }
  }

  // Check physical push button on D6 (Active LOW with INPUT_PULLUP)
  if (digitalRead(PIN_BUTTON) == LOW) {
    unsigned long now = millis();
    if (now - lastBtnPressTime > DEBOUNCE_DELAY_MS) {
      lastBtnPressTime = now;
      triggerPhysicalButtonScan();
    }
  }

  // Small delay to prevent tight spin
  delay(5);
}
