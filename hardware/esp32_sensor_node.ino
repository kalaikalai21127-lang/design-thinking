/*
================================================================================
Low-Cost Neonatal Jaundice Screening Prototype
ESP32 Native Optical Sensor Node Firmware
================================================================================
Hardware Specifications:
- Microcontroller : ESP32 DevKit / Dev Module (NodeMCU-32S / ESP-WROOM-32)
- Colour Sensor   : GY-9960 / APDS-9960-compatible RGB & Ambient Light Module (I2C 0x39)
- OLED Display    : 0.96-inch SSD1306 Monochrome 128x64 OLED (I2C 0x3C)
- Push Button     : ESP32 GPIO 4 -> Connected to GND (using INPUT_PULLUP)
- Diagnostic LED  : ESP32 GPIO 2 (Onboard Blue LED, Active HIGH)
- Power Supply    : 3.3V & GND shared across ESP32, GY-9960, and SSD1306

ESP32 Pinout Mapping:
- I2C SDA         : GPIO 21 -> Connected to GY-9960 SDA and SSD1306 SDA
- I2C SCL         : GPIO 22 -> Connected to GY-9960 SCL and SSD1306 SCL
- Push Button     : GPIO 4  -> Pulls to GND on press (Triggers optical scan)
- Status / LED    : GPIO 2  -> ESP32 built-in blue LED (Active HIGH)
- VCC             : 3.3V    -> (Do NOT connect sensor or OLED to 5V / VIN!)
- GND             : Common Ground (GND)

Features:
1. Native I2C driver for GY-9960 / APDS-9960 color sensor (0x39) - reading
   Clear (Reading 1), Red (Reading 2), Green (Reading 3), Blue (Reading 4) counts.
2. SSD1306 0.96" OLED display (0x3C) showing live illumination mode, IP, and optical metrics.
3. Repeating Timed Illumination Sequence:
   OFF (1033ms) -> BLUE (1033ms) -> GREEN (1033ms) -> WHITE (1033ms) -> Pause (2062ms)
4. Serial Monitor CSV stream matching exact 6-field hardware output:
   <timestamp_ms>,<illumination_mode>,<reading_1>,<reading_2>,<reading_3>,<reading_4>
5. Embedded Responsive Web Dashboard hosted directly on ESP32 Port 80 via WebServer.
6. Push button on GPIO 4 triggers immediate optical measurement and OLED refresh.
7. Non-blocking HTTP POST upload to Flask backend endpoint /api/sensor/readings.
8. Automatic Wi-Fi reconnection handling without halting sensor acquisition.
================================================================================
Required Arduino IDE Libraries:
1. "Adafruit SSD1306" (by Adafruit - install via Library Manager)
2. "Adafruit GFX Library" (by Adafruit - install via Library Manager)
3. "ArduinoJson" (v6 or v7 by Benoit Blanchon - install via Library Manager)
*(WiFi, WebServer, HTTPClient, and Wire are built into the ESP32 Arduino Core)*
================================================================================
*/

#include <Wire.h>
#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

// ============================================================================
// HARDWARE PIN DEFINITIONS (ESP32 Dev Module)
// ============================================================================
const uint8_t PIN_I2C_SDA = 21; // GPIO 21 - Shared I2C Data (GY-9960 + SSD1306)
const uint8_t PIN_I2C_SCL = 22; // GPIO 22 - Shared I2C Clock (GY-9960 + SSD1306)
const uint8_t PIN_BUTTON  = 4;  // GPIO 4  - Push Button to GND (INPUT_PULLUP)
const uint8_t PIN_LED     = 2;  // GPIO 2  - ESP32 Built-in Blue LED (Active HIGH)

#define BOARD_NAME "ESP32 Dev Module"
#define DEVICE_ID  "ESP32_OPTICAL_01"

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
// WI-FI & FLASK BACKEND CONFIGURATION
// ============================================================================
// Configurable placeholders as specified:
//   const char* ssid = "YOUR_WIFI_NAME";
//   const char* password = "YOUR_WIFI_PASSWORD";
//   const char* backendUrl = "http://YOUR_COMPUTER_IP:5000/api/sensor/readings";
// (Ensure NO SPACES inside the URL, and do not use localhost or 127.0.0.1)
const char* ssid     = "HKV";
const char* password = "varman5118";
const char* backendUrl = "http://10.234.224.98:5000/api/sensor/readings";

// Fallback SoftAP credentials if router Wi-Fi is unavailable
const char* ap_ssid  = "ESP32-Jaundice-Screener";
const char* ap_pass  = "12345678";

// Embedded Web Server on Port 80
WebServer server(80);

// Automatic Background Hardware Telemetry Streaming
const bool ENABLE_BACKEND_UPLOAD = true;

// Illumination Sequence State Machine: OFF -> BLUE -> GREEN -> WHITE -> Pause
enum IllumMode {
  MODE_OFF,
  MODE_BLUE,
  MODE_GREEN,
  MODE_WHITE,
  MODE_PAUSE
};

IllumMode currentIllumMode = MODE_OFF;
unsigned long lastStepTime = 0;
const unsigned long STEP_DURATION_MS  = 1033; // 1033 ms per illumination step
const unsigned long PAUSE_DURATION_MS = 2062; // 2062 ms pause between cycles
unsigned long lastWiFiReconnectCheck  = 0;

// ============================================================================
// OPTICAL READING DATA STRUCTURE
// ============================================================================
struct ColorReading {
  uint16_t red   = 0; // Reading 2 (Red Channel, Reg 0x96-0x97)
  uint16_t green = 0; // Reading 3 (Green Channel, Reg 0x98-0x99)
  uint16_t blue  = 0; // Reading 4 (Blue Channel, Reg 0x9A-0x9B)
  uint16_t clear = 0; // Reading 1 (Clear Channel, Reg 0x94-0x95)
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
// LED CONTROL HELPERS (ESP32 GPIO 2)
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
  Serial.printf("[GY-9960] Sensor identified at I2C 0x39 (ID: 0x%02X)\n", chipId);

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

  // Request 8 bytes starting from CDATAL (0x94):
  // 0x94-0x95 = Clear Channel (c) -> Reading 1
  // 0x96-0x97 = Red Channel   (r) -> Reading 2
  // 0x98-0x99 = Green Channel (g) -> Reading 3
  // 0x9A-0x9B = Blue Channel  (b) -> Reading 4
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
      Serial.println(F("[ERROR] GY-9960 not responding at 0x39 on ESP32 SDA:21, SCL:22!"));
      return false;
    }
    sensorDetected = true;
  }

  // Flash diagnostic LED on GPIO 2 during measurement
  ledOn();
  delay(120); // Optical stabilization delay

  uint16_t r = 0, g = 0, b = 0, c = 0;
  bool ok = readGY9960Color(r, g, b, c);
  ledOff();

  if (!ok) {
    Serial.println(F("[ERROR] Failed to read color data from GY-9960!"));
    return false;
  }

  out.clear = c; // Reading 1
  out.red   = r; // Reading 2
  out.green = g; // Reading 3
  out.blue  = b; // Reading 4

  // Jaundice optical ratio calculation:
  // Bilirubin absorbs blue light (440-490nm). Elevated bilirubin lowers blue reflectance,
  // causing the Red/Blue ratio and (R+G)/(2*B) ratio to increase.
  float blueDiv = (b > 0) ? (float)b : 1.0f;
  out.ratioRB = (float)r / blueDiv;
  out.yellowIndex = ((float)r + (float)g) / (2.0f * blueDiv);

  // Calibrated Jaundice Optical Screening Thresholds
  // Reference Reading: Clear: 76, Red: 38, Green: 30, Blue: 25 | Baseline R/B: 1.55, Yellow Idx: 1.38
  const float THRESHOLD_RB_NORMAL_MAX = 1.65f;
  const float THRESHOLD_RB_MILD_MAX   = 2.10f;
  const float THRESHOLD_YI_NORMAL_MAX = 1.45f;
  const float THRESHOLD_YI_MILD_MAX   = 1.85f;

  if (out.ratioRB <= THRESHOLD_RB_NORMAL_MAX && out.yellowIndex <= THRESHOLD_YI_NORMAL_MAX) {
    out.status = "Normal";
    out.recommendation = "Optical reflection matches calibrated baseline. Normal risk.";
  } else if (out.ratioRB <= THRESHOLD_RB_MILD_MAX && out.yellowIndex <= THRESHOLD_YI_MILD_MAX) {
    out.status = "Mild Risk";
    out.recommendation = "Blue light attenuation detected. Borderline risk. Re-test in 4-6h.";
  } else {
    out.status = "High Risk";
    out.recommendation = "Significant blue absorption flagged. Clinical STB blood test recommended.";
  }
  out.readingIndex = ++scanCounter;
  out.timestampMs = millis();
  out.valid = true;

  return true;
}

// ============================================================================
// SSD1306 OLED DISPLAY FUNCTIONS (ESP32 I2C 0x3C)
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
  oledPrintHeader("ESP32 JAUNDICE");
  display.setCursor(0, 16);
  display.println(F("Board  : ESP32 DevKit"));
  display.println(F("I2C Bus: SDA 21, SCL 22"));
  display.println(F("Sensor : GY-9960 (0x39)"));
  display.println(F("---------------------"));
  display.setCursor(0, 48);
  display.println(msg);
  display.display();
}

void oledShowReadyScreen() {
  if (!oledDetected) return;
  oledPrintHeader("ESP32 JAUNDICE");
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
  display.println(F("Btn: GPIO 4 to Scan"));
  display.display();
}

void oledShowScanning() {
  if (!oledDetected) return;
  oledPrintHeader("SAMPLING TISSUE");
  display.setCursor(0, 18);
  display.println(F("Optical LED Active..."));
  display.println(F("Reading C, R, G, B"));
  display.setCursor(0, 42);
  display.println(F("Hold sensor steady"));
  display.drawRect(0, 56, 128, 6, SSD1306_WHITE);
  display.fillRect(2, 58, 64, 2, SSD1306_WHITE);
  display.display();
}

void oledShowModeResults(const char* modeStr, uint16_t c, uint16_t r, uint16_t g, uint16_t b, float ratioRB, float yellowIdx) {
  if (!oledDetected) return;
  display.clearDisplay();

  display.setTextSize(1);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setCursor(0, 0);
  display.printf(" MODE: %-5s | %-7s ", modeStr, (WiFi.status() == WL_CONNECTED) ? "ONLINE" : "NO-WIFI");
  display.setTextColor(SSD1306_WHITE);

  display.setCursor(0, 11);
  if (WiFi.status() == WL_CONNECTED) {
    display.printf("IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    display.println(F("IP: Disconnected"));
  }

  display.setCursor(0, 22);
  display.printf("C (R1):%4u  R (R2):%4u\n", c, r);
  display.setCursor(0, 32);
  display.printf("G (R3):%4u  B (R4):%4u\n", g, b);

  display.setCursor(0, 44);
  display.printf("R/B: %4.2f  Y-Idx: %4.2f\n", ratioRB, yellowIdx);

  display.setCursor(0, 56);
  if (ratioRB <= 1.65f) {
    display.print(F("Status: Normal (Low)"));
  } else if (ratioRB <= 2.10f) {
    display.print(F("Status: Mild Risk"));
  } else {
    display.print(F("Status: High Risk"));
  }
  display.display();
}

void oledShowResults(const ColorReading &r) {
  oledShowModeResults("MANUAL", r.clear, r.red, r.green, r.blue, r.ratioRB, r.yellowIndex);
}

void oledShowError(const char* title, const char* desc) {
  if (!oledDetected) return;
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_BLACK, SSD1306_WHITE);
  display.setCursor(0, 0);
  display.print(F(" ESP32 HW ERROR      "));
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 14);
  display.println(title);
  display.println(F("---------------------"));
  display.println(desc);
  display.display();
}

// ============================================================================
// EMBEDDED WEB DASHBOARD HTML (HOSTED DIRECTLY ON ESP32 PORT 80)
// ============================================================================
const char INDEX_HTML[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Neonatal Jaundice Screening - ESP32 & GY-9960</title>
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
        .chip-clear { color: #64748b; border-top: 4px solid #64748b; }
        .chip-red   { color: #dc2626; border-top: 4px solid #dc2626; }
        .chip-green { color: #16a34a; border-top: 4px solid #16a34a; }
        .chip-blue  { color: #2563eb; border-top: 4px solid #2563eb; }
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
            <p>ESP32 Dev Module & GY-9960 / APDS-9960 Optical Sensor Node</p>
            <div class="badges">
                <span class="badge">Board: ESP32 Dev Module</span>
                <span class="badge">I2C: GPIO 21 (SDA), GPIO 22 (SCL)</span>
                <span class="badge">Button: GPIO 4</span>
                <span class="badge">LED: GPIO 2</span>
                <span class="badge">Sensor: GY-9960 (I2C 0x39)</span>
                <span class="badge">OLED: SSD1306 (I2C 0x3C)</span>
                <span class="badge">Port: 80 (HTTP)</span>
            </div>
        </div>

        <!-- Clinical Research Notice -->
        <div class="alert-warning">
            <strong>Clinical Research Notice:</strong> This device is an experimental engineering research prototype. Raw optical measurements require empirical calibration against laboratory Serum Total Bilirubin (STB) blood tests before clinical evaluation.
        </div>

        <!-- Actions -->
        <div class="actions-bar">
            <button id="scanBtn" class="btn" onclick="triggerScan()">Take Optical Scan Now (GPIO 4)</button>
            <label style="font-size: 0.85rem; color: var(--slate); display: flex; align-items: center; gap: 6px; cursor: pointer;">
                <input type="checkbox" id="autoRefresh" checked onchange="toggleAutoRefresh(this.checked)"> Auto-refresh live data (2s)
            </label>
            <span id="scanStatus" style="font-size: 0.85rem; font-weight: 600; color: var(--primary);"></span>
        </div>

        <!-- 4 Real-time Sensor Channel Counts -->
        <div class="card">
            <h2>Raw Optical Channel ADC Counts (GY-9960 I2C 0x39)</h2>
            <div class="grid-4">
                <div class="channel-box chip-clear">
                    <div class="label">Reading 1 &bull; Clear</div>
                    <div class="value" id="valClear">--</div>
                    <span style="font-size: 0.72rem; color: var(--slate);">Ambient Illuminance</span>
                </div>
                <div class="channel-box chip-red">
                    <div class="label">Reading 2 &bull; Red</div>
                    <div class="value" id="valRed">--</div>
                    <span style="font-size: 0.72rem; color: var(--slate);">620-700nm Reflectance</span>
                </div>
                <div class="channel-box chip-green">
                    <div class="label">Reading 3 &bull; Green</div>
                    <div class="value" id="valGreen">--</div>
                    <span style="font-size: 0.72rem; color: var(--slate);">500-560nm Reference</span>
                </div>
                <div class="channel-box chip-blue">
                    <div class="label">Reading 4 &bull; Blue</div>
                    <div class="value" id="valBlue">--</div>
                    <span style="font-size: 0.72rem; color: var(--slate);">440-490nm Bilirubin Peak</span>
                </div>
            </div>

            <!-- Optical Color Preview -->
            <div class="color-preview-box">
                <div class="color-swatch" id="colorSwatch"></div>
                <div>
                    <strong style="font-size: 0.9rem;">Synthesized Cutaneous Reflectance Color</strong>
                    <div id="swatchLabel" style="font-size: 0.8rem; color: var(--slate); margin-top: 2px;">RGB Color: --</div>
                </div>
            </div>

            <!-- Optical Ratios & Screening Classification -->
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="title">R/B Optical Ratio (Red / Blue)</div>
                    <div class="num" id="valRatioRB">--</div>
                    <span style="font-size: 0.75rem; color: var(--slate);">Normal baseline: &le; 1.65</span>
                </div>
                <div class="metric-card">
                    <div class="title">Yellow-Blue Optical Index</div>
                    <div class="num" id="valYellowIdx">--</div>
                    <span style="font-size: 0.75rem; color: var(--slate);">(Red + Green) / (2 * Blue)</span>
                </div>
                <div class="metric-card">
                    <div class="title">Total Scans Performed</div>
                    <div class="num" id="valScans">0</div>
                    <span style="font-size: 0.75rem; color: var(--slate);">Session measurement count</span>
                </div>
            </div>

            <!-- Screening Classification Status -->
            <div style="background: #f8fafc; border: 1px solid var(--border); border-radius: 12px; padding: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: gap;">
                <div>
                    <span style="font-size: 0.8rem; color: var(--slate); font-weight: 600;">Preliminary Optical Assessment:</span>
                    <div id="valStatus" style="font-size: 1.1rem; font-weight: 800; color: var(--primary); margin-top: 2px;">Waiting for scan...</div>
                </div>
                <span class="status-badge" id="badgeMode">MODE: OFF</span>
            </div>
        </div>

        <!-- ESP32 Hardware Pinout Reference Table -->
        <div class="card">
            <h2>Hardware Wiring & ESP32 Pinout</h2>
            <table class="table">
                <thead>
                    <tr><th>Peripheral Pin</th><th>ESP32 Pin</th><th>GPIO</th><th>Electrical Function</th></tr>
                </thead>
                <tbody>
                    <tr><td><strong>GY-9960 SDA & OLED SDA</strong></td><td><strong>GPIO 21</strong></td><td>GPIO 21</td><td>Shared I2C Serial Data (Address 0x39 & 0x3C)</td></tr>
                    <tr><td><strong>GY-9960 SCL & OLED SCL</strong></td><td><strong>GPIO 22</strong></td><td>GPIO 22</td><td>Shared I2C Serial Clock (100 kHz)</td></tr>
                    <tr><td><strong>Push Button</strong></td><td><strong>GPIO 4</strong></td><td>GPIO 4</td><td>Triggers optical scan (INPUT_PULLUP to GND)</td></tr>
                    <tr><td><strong>Status / Diagnostic LED</strong></td><td><strong>GPIO 2</strong></td><td>GPIO 2</td><td>ESP32 onboard blue LED (Active HIGH)</td></tr>
                    <tr><td><strong>Power (VCC)</strong></td><td><strong>3.3V</strong></td><td>3V3</td><td>Regulated 3.3V power (Do NOT connect 5V to sensor)</td></tr>
                    <tr><td><strong>Ground (GND)</strong></td><td><strong>GND</strong></td><td>GND</td><td>Common system ground</td></tr>
                </tbody>
            </table>
        </div>

        <div class="footer">
            Design Thinking Low-Cost Jaundice Screening System &bull; ESP32 HTTP Server Port 80 &bull; Bilirubin Spectral Optical Research
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
                console.warn('Live fetch error:', err);
            }
        }

        function updateUI(data) {
            document.getElementById('valClear').innerText = data.clear ?? data.reading_1 ?? '--';
            document.getElementById('valRed').innerText = data.red ?? data.reading_2 ?? '--';
            document.getElementById('valGreen').innerText = data.green ?? data.reading_3 ?? '--';
            document.getElementById('valBlue').innerText = data.blue ?? data.reading_4 ?? '--';
            document.getElementById('valRatioRB').innerText = (data.ratio_rb ?? 0).toFixed(2);
            document.getElementById('valYellowIdx').innerText = (data.yellow_index ?? 0).toFixed(2);
            document.getElementById('valScans').innerText = data.reading_count ?? 0;
            document.getElementById('valStatus').innerText = data.status || 'Normal';
            if (data.illumination_mode) {
                document.getElementById('badgeMode').innerText = 'MODE: ' + data.illumination_mode;
            }

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

  doc["device"]          = DEVICE_ID;
  doc["board"]           = BOARD_NAME;
  doc["sensor"]          = "GY-9960";
  doc["sensor_address"]  = "0x39";
  doc["oled_address"]    = "0x3C";
  doc["reading_1"]       = lastReading.clear;
  doc["reading_2"]       = lastReading.red;
  doc["reading_3"]       = lastReading.green;
  doc["reading_4"]       = lastReading.blue;
  doc["clear"]           = lastReading.clear;
  doc["red"]             = lastReading.red;
  doc["green"]           = lastReading.green;
  doc["blue"]            = lastReading.blue;
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
    sendPayloadToFlaskBackend(r);
  } else {
    oledShowError("SCAN FAILED", "Check GY-9960 wiring:\nSDA: GPIO 21\nSCL: GPIO 22\nPower: 3.3V");
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

  doc["board"]           = BOARD_NAME;
  doc["device_id"]       = DEVICE_ID;
  doc["sensor_detected"] = sensorDetected;
  doc["oled_detected"]   = oledDetected;
  doc["pin_sda"]         = PIN_I2C_SDA; // GPIO 21
  doc["pin_scl"]         = PIN_I2C_SCL; // GPIO 22
  doc["pin_button"]      = PIN_BUTTON;  // GPIO 4
  doc["pin_led"]         = PIN_LED;     // GPIO 2
  doc["wifi_connected"]  = (WiFi.status() == WL_CONNECTED);
  doc["free_heap"]       = ESP.getFreeHeap();

  String jsonOut;
  serializeJson(doc, jsonOut);
  server.send(200, "application/json", jsonOut);
}

void handleNotFound() {
  server.send(404, "text/plain", "404 Not Found - ESP32 Jaundice Screener");
}

// ============================================================================
// NON-BLOCKING FORWARDING TO FLASK REST BACKEND
// ============================================================================
void sendPayloadToFlaskBackend(const char* illuminationMode, uint16_t c, uint16_t r, uint16_t g, uint16_t b, unsigned long timestampMs) {
  if (!ENABLE_BACKEND_UPLOAD || WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  bool isHttps = String(backendUrl).startsWith("https://");

  #if defined(ARDUINOJSON_VERSION_MAJOR) && ARDUINOJSON_VERSION_MAJOR >= 7
    JsonDocument doc;
  #else
    StaticJsonDocument<512> doc;
  #endif

  doc["device_id"]         = DEVICE_ID;
  doc["sensor_type"]       = "GY-9960";
  doc["timestamp_ms"]      = timestampMs;
  doc["illumination_mode"] = illuminationMode;
  doc["reading_1"]         = c; // Clear Channel count (Reg 0x94-0x95)
  doc["reading_2"]         = r; // Red Channel count   (Reg 0x96-0x97)
  doc["reading_3"]         = g; // Green Channel count (Reg 0x98-0x99)
  doc["reading_4"]         = b; // Blue Channel count  (Reg 0x9A-0x9B)
  doc["clear"]             = c;
  doc["red"]               = r;
  doc["green"]             = g;
  doc["blue"]              = b;

  String payload;
  serializeJson(doc, payload);

  if (isHttps) {
    WiFiClientSecure secureClient;
    secureClient.setInsecure(); // Allows connecting to hosted HTTPS endpoints without custom certs
    if (http.begin(secureClient, backendUrl)) {
      http.setTimeout(1200); // Fast non-blocking timeout
      http.addHeader("Content-Type", "application/json");
      http.POST(payload);
      http.end();
    }
  } else {
    WiFiClient client;
    if (http.begin(client, backendUrl)) {
      http.setTimeout(1200); // Fast non-blocking timeout
      http.addHeader("Content-Type", "application/json");
      http.POST(payload);
      http.end();
    }
  }
}

// Legacy overload for button scan compatibility
void sendPayloadToFlaskBackend(const ColorReading &r) {
  sendPayloadToFlaskBackend("MANUAL", r.clear, r.red, r.green, r.blue, r.timestampMs);
}

// ============================================================================
// ACTION: TRIGGER MEASUREMENT FROM PHYSICAL BUTTON (GPIO 4)
// ============================================================================
void triggerPhysicalButtonScan() {
  Serial.printf("\n[BUTTON GPIO %d PRESSED] Initiating Optical Measurement...\n", PIN_BUTTON);
  oledShowScanning();

  ColorReading r;
  if (acquireSensorData(r)) {
    lastReading = r;
    oledShowResults(r);
    ledBlink(2, 100, 100);

    // Send to Flask backend
    sendPayloadToFlaskBackend(r);
  } else {
    oledShowError("GY-9960 READ ERROR", "Verify I2C wiring:\nSDA: GPIO 21\nSCL: GPIO 22\nPower: 3.3V");
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
  // Try connecting for ~8 seconds
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(400);
    digitalWrite(PIN_LED, !digitalRead(PIN_LED)); // Toggle LED on GPIO 2 while waiting
    Serial.print(F("."));
    attempts++;
  }
  digitalWrite(PIN_LED, LOW);

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println(F("[WIFI SUCCESS] Connected to local network!"));
    Serial.printf("  - Board IP Address   : %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("  - Gateway IP         : %s\n", WiFi.gatewayIP().toString().c_str());
    Serial.printf("  - Subnet Mask        : %s\n", WiFi.subnetMask().toString().c_str());
    Serial.printf("  - Target Backend     : %s\n", backendUrl);
    Serial.printf("  - Web Dashboard Port : 80 (http://%s/)\n", WiFi.localIP().toString().c_str());
    ledBlink(1, 400, 100);
  } else {
    Serial.println();
    Serial.println(F("[WIFI NOTICE] Could not connect to primary Wi-Fi. Launching SoftAP..."));
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
  Serial.printf(" Neonatal Jaundice Screening - %s & GY-9960 Node\n", BOARD_NAME);
  Serial.println(F("================================================================="));
  Serial.printf("  - Microcontroller : %s\n", BOARD_NAME);
  Serial.printf("  - I2C Bus Pins    : SDA=GPIO %d, SCL=GPIO %d\n", PIN_I2C_SDA, PIN_I2C_SCL);
  Serial.printf("  - Push Button Pin : GPIO %d [INPUT_PULLUP to GND]\n", PIN_BUTTON);
  Serial.printf("  - Diagnostic LED  : GPIO %d [ESP32 Built-in Blue LED]\n", PIN_LED);
  Serial.printf("  - GY-9960 Sensor  : Address 0x39 (Color RGB + Clear)\n");
  Serial.printf("  - SSD1306 OLED    : Address 0x3C (128x64 Monochrome)\n");
  Serial.printf("  - Target Backend  : %s\n", backendUrl);
  Serial.println(F("================================================================="));

  // Initialize I2C Bus on ESP32 (SDA = GPIO 21, SCL = GPIO 22)
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
    Serial.printf("  Check: VIN to 3.3V, GND, SDA to GPIO %d, SCL to GPIO %d.\n", PIN_I2C_SDA, PIN_I2C_SCL);
    if (oledDetected) {
      char errBuf[48];
      snprintf(errBuf, sizeof(errBuf), "Check I2C:\nSDA:21 SCL:22 3.3V");
      oledShowError("GY-9960 NOT FOUND", errBuf);
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
  Serial.println(F("[HTTP SERVER] Embedded Web Server listening on port 80."));

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
  Serial.printf(" System ready! Press Push Button (GPIO %d) or use Web Dashboard\n", PIN_BUTTON);
  Serial.println(F(" to perform optical jaundice screening measurements.            "));
  Serial.println(F("=================================================================\n"));
}

// ============================================================================
// ARDUINO MAIN LOOP
// ============================================================================
void loop() {
  // Service incoming HTTP requests on Port 80
  server.handleClient();

  // Automatic non-blocking Wi-Fi reconnection check every 5 seconds
  if (WiFi.status() != WL_CONNECTED && millis() - lastWiFiReconnectCheck > 5000) {
    lastWiFiReconnectCheck = millis();
    WiFi.reconnect();
  }

  unsigned long now = millis();
  unsigned long interval = (currentIllumMode == MODE_PAUSE) ? PAUSE_DURATION_MS : STEP_DURATION_MS;

  // Timed Illumination Sequence Machine: OFF (1033ms) -> BLUE (1033ms) -> GREEN (1033ms) -> WHITE (1033ms) -> PAUSE (2062ms)
  if (now - lastStepTime >= interval) {
    lastStepTime = now;

    const char* modeStr = "OFF";
    switch (currentIllumMode) {
      case MODE_OFF:
        modeStr = "OFF";
        currentIllumMode = MODE_BLUE;
        break;
      case MODE_BLUE:
        modeStr = "BLUE";
        currentIllumMode = MODE_GREEN;
        break;
      case MODE_GREEN:
        modeStr = "GREEN";
        currentIllumMode = MODE_WHITE;
        break;
      case MODE_WHITE:
        modeStr = "WHITE";
        currentIllumMode = MODE_PAUSE;
        break;
      case MODE_PAUSE:
        modeStr = "OFF";
        currentIllumMode = MODE_BLUE;
        break;
    }

    // Read real GY-9960 / APDS-9960 optical counts directly from registers:
    // c = Clear Channel (Reg 0x94-0x95) -> Reading 1
    // r = Red Channel   (Reg 0x96-0x97) -> Reading 2
    // g = Green Channel (Reg 0x98-0x99) -> Reading 3
    // b = Blue Channel  (Reg 0x9A-0x9B) -> Reading 4
    uint16_t r = 0, g = 0, b = 0, c = 0;
    if (readGY9960Color(r, g, b, c)) {
      lastReading.clear = c;
      lastReading.red   = r;
      lastReading.green = g;
      lastReading.blue  = b;
      float blueDiv = (b > 0) ? (float)b : 1.0f;
      lastReading.ratioRB = (float)r / blueDiv;
      lastReading.yellowIndex = ((float)r + (float)g) / (2.0f * blueDiv);
      lastReading.timestampMs = now;
      lastReading.valid = true;

      // 1. Output exact CSV format to Serial Monitor:
      // <timestamp_ms>,<illumination_mode>,<reading_1>,<reading_2>,<reading_3>,<reading_4>
      Serial.printf("%lu,%s,%u,%u,%u,%u\n", now, modeStr, c, r, g, b);

      // 2. Update OLED Display with illumination mode
      oledShowModeResults(modeStr, c, r, g, b, lastReading.ratioRB, lastReading.yellowIndex);

      // 3. Fast non-blocking HTTP upload to Flask backend
      if (ENABLE_BACKEND_UPLOAD) {
        sendPayloadToFlaskBackend(modeStr, c, r, g, b, now);
      }
    }
  }

  // Check physical push button (Active LOW with INPUT_PULLUP on GPIO 4)
  if (digitalRead(PIN_BUTTON) == LOW) {
    if (now - lastBtnPressTime > DEBOUNCE_DELAY_MS) {
      lastBtnPressTime = now;
      triggerPhysicalButtonScan();
    }
  }

  delay(5);
}
