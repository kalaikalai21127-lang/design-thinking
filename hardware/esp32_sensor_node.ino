/*
================================================================================
Smart Jaundice Screening System Using Optical Sensor Readings
ESP32 Microcontroller Firmware Sketch (Future Hardware Integration Node)
================================================================================
Hardware Components:
- ESP32 Development Board
- TCS34725 / TCS3200 Color Optical Sensor
- High-Intensity White / 460nm Blue LED Light Source
- LDR / Photodiode Transmittance Receiver
================================================================================
Circuit Architecture:
LED Light Source ---> Tissue/Finger ---> Optical Sensor ---> ESP32 ADC/I2C ---> Flask REST API
================================================================================
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Wi-Fi Credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Flask Backend REST API Endpoint URL
const char* serverUrl = "http://192.168.1.100:5000/api/predict";

// Pin Definitions
const int LED_PIN = 2;          // Diagnostic LED Light Pin
const int SENSOR_PIN = 34;      // Analog Optical Sensor / Photodiode Pin (ADC 0-4095)

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  pinMode(SENSOR_PIN, INPUT);

  // Connect to Wi-Fi
  Serial.println("\n[ESP32] Connecting to Wi-Fi Network...");
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n[ESP32] Wi-Fi Connected!");
  Serial.print("[ESP32] IP Address: ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 1. Turn on Diagnostic Optical LED Light
  digitalWrite(LED_PIN, HIGH);
  delay(100);

  // 2. Read Raw Analog Value from Optical Sensor (0 - 4095)
  int rawAnalog = analogRead(SENSOR_PIN);

  // 3. Map ADC 12-bit (0-4095) to Standardized 8-bit Optical Reading (0 - 255)
  int normalizedReading = map(rawAnalog, 0, 4095, 0, 255);

  // 4. Turn off Diagnostic LED Light
  digitalWrite(LED_PIN, LOW);

  Serial.print("[ESP32] Raw Optical Analog Reading: ");
  Serial.print(rawAnalog);
  Serial.print(" | Normalized (0-255): ");
  Serial.println(normalizedReading);

  // 5. Send POST HTTP Request to Flask REST API
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");

    // Construct JSON Payload
    StaticJsonDocument<200> doc;
    doc["sensor_value"] = normalizedReading;
    doc["name"] = "Hardware ESP32 Sensor Node 01";
    doc["age"] = 0;
    doc["gender"] = "Hardware Node";

    String jsonPayload;
    serializeJson(doc, jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.print("[HTTP SUCCESS] Response Code: ");
      Serial.println(httpResponseCode);
      Serial.println("[HTTP RESPONSE] " + response);
    } else {
      Serial.print("[HTTP ERROR] Failed to send POST. Code: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  }

  // Delay 10 seconds before next sensor scan
  delay(10000);
}
