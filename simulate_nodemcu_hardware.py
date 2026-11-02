"""
================================================================================
NodeMCU ESP8266 & GY-9960 Hardware Node Simulator
================================================================================
This script simulates physical NodeMCU ESP8266 hardware reading optical counts
from the GY-9960 / APDS-9960 colour sensor and streaming payloads to the Flask
backend API (Localhost, LAN IP, or Cloud Hosted URL like Render/Railway).
================================================================================
"""

import sys
import time
import random
import json
import argparse
import urllib.request
import urllib.error

def simulate_optical_scan(scan_num, backend_url):
    # Simulated tissue optical reflection counts
    # Healthy tissue vs Jaundiced tissue (where blue light is absorbed by bilirubin)
    is_jaundiced = (scan_num % 2 == 0)
    
    if is_jaundiced:
        # High blue absorption -> Lower blue counts -> Higher R/B ratio
        red = random.randint(480, 560)
        green = random.randint(390, 470)
        blue = random.randint(110, 180)  # Attenuated by bilirubin
        clear = red + green + blue + random.randint(50, 100)
    else:
        # Normal optical reflection
        red = random.randint(350, 420)
        green = random.randint(340, 410)
        blue = random.randint(290, 360)
        clear = red + green + blue + random.randint(50, 100)

    ratio_rb = round(red / max(1, blue), 2)
    yellow_index = round((red + green) / (2.0 * max(1, blue)), 2)

    payload = {
        "device_id": "NodeMCU_ESP8266_GY9960_Sim",
        "sensor_type": "GY-9960",
        "name": f"NodeMCU Subject #{scan_num}",
        "red": red,
        "green": green,
        "blue": blue,
        "clear": clear,
        "ratio_rb": ratio_rb,
        "yellow_index": yellow_index,
        "age": 0,
        "gender": "Hardware Node"
    }

    print(f"\n=======================================================")
    print(f"[SIMULATOR] SCAN #{scan_num} Triggered (Simulating Button D6 / Scan)")
    print(f"=======================================================")
    print(f"  Sensor Model     : GY-9960 (APDS-9960 compatible, I2C 0x39)")
    print(f"  OLED Display     : SSD1306 (128x64, I2C 0x3C)")
    print(f"  Red Channel      : {red} counts (620-700nm)")
    print(f"  Green Channel    : {green} counts (500-560nm)")
    print(f"  Blue Channel     : {blue} counts (440-490nm) <-- Bilirubin Absorption")
    print(f"  Clear Channel    : {clear} counts (Ambient / Total)")
    print(f"  R/B Optical Ratio: {ratio_rb}")
    print(f"  Yellow-Blue Idx  : {yellow_index}")
    print(f"[HTTP] Transmitting payload to Backend: {backend_url}")

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            backend_url,
            data=req_data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'ESP8266-Simulator/1.0'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            status_code = response.getcode()
            resp_body = response.read().decode('utf-8')
            data = json.loads(resp_body)
            print(f"[HTTP SUCCESS {status_code}] Record ID #{data.get('id')}")
            print(f"  Status          : {data.get('status')}")
            print(f"  Recommendation  : {data.get('recommendation')}")
    except Exception as e:
        print(f"[HTTP ERROR] Failed to connect to {backend_url}: {e}")
        print("  Ensure your backend is running and the URL is reachable!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate NodeMCU sensor readings to backend.")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/predict", help="Backend API endpoint URL (default: http://127.0.0.1:5000/api/predict)")
    parser.add_argument("--count", type=int, default=3, help="Number of scans to simulate (default: 3, 0 for continuous)")
    parser.add_argument("--interval", type=float, default=1.5, help="Interval in seconds between scans (default: 1.5)")
    args = parser.parse_args()

    print("[INIT] Starting NodeMCU ESP8266 & GY-9960 Sensor Node Simulation...")
    print(f"[INFO] Target Backend URL: {args.url}")
    print(f"[INFO] Scan count: {'Continuous' if args.count == 0 else args.count}, Interval: {args.interval}s")

    i = 1
    try:
        while True:
            simulate_optical_scan(i, args.url)
            if args.count > 0 and i >= args.count:
                break
            i += 1
            time.sleep(args.interval)
        print(f"\n[SUCCESS] Simulation finished! Access the dashboard to view results.")
    except KeyboardInterrupt:
        print("\n[STOPPED] Simulation stopped by user.")
