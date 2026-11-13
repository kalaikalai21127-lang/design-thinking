"""
================================================================================
ESP32 & NodeMCU Optical Sensor Node Simulator (GY-9960 / APDS-9960)
================================================================================
Simulates physical ESP32 optical sensor hardware running the illumination
sequence (OFF -> BLUE -> GREEN -> WHITE) and streaming real sensor packets to:
POST /api/sensor/readings

Output matches Serial Monitor CSV format:
<timestamp_ms>,<illumination_mode>,<reading_1>,<reading_2>,<reading_3>,<reading_4>
Where:
- reading_1 = Clear counts (c, Registers 0x94-0x95)
- reading_2 = Red counts   (r, Registers 0x96-0x97)
- reading_3 = Green counts (g, Registers 0x98-0x99)
- reading_4 = Blue counts  (b, Registers 0x9A-0x9B)
================================================================================
"""

import sys
import time
import random
import json
import argparse
import urllib.request
import urllib.error

ILLUMINATION_MODES = ["OFF", "BLUE", "GREEN", "WHITE"]

def simulate_step(step_idx, mode, backend_url, start_time_ms):
    now_ms = int(time.time() * 1000) - start_time_ms + 260300

    # Optical reflectance values matching calibrated readings:
    # Baseline: Clear: 76, Red: 38, Green: 30, Blue: 25
    clear = 76 + random.randint(-1, 2)
    red   = 38 + random.randint(-1, 1)
    green = 30 + random.randint(-1, 1)
    blue  = 25 + random.randint(-1, 1)

    # 1. Serial Monitor CSV output (Exact 6 fields)
    csv_line = f"{now_ms},{mode},{clear},{red},{green},{blue}"
    print(f"[SERIAL] {csv_line}")

    # 2. JSON Payload for POST /api/sensor/readings
    payload = {
        "device_id": "ESP32_OPTICAL_01",
        "sensor_type": "GY-9960",
        "timestamp_ms": now_ms,
        "illumination_mode": mode,
        "reading_1": clear,
        "reading_2": red,
        "reading_3": green,
        "reading_4": blue
    }

    try:
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            backend_url,
            data=req_data,
            headers={'Content-Type': 'application/json', 'User-Agent': 'ESP32-SensorNode/1.0'}
        )
        with urllib.request.urlopen(req, timeout=3) as response:
            status_code = response.getcode()
            resp_body = response.read().decode('utf-8')
            data = json.loads(resp_body)
            print(f"  -> [HTTP {status_code}] Mode: {mode} | Status: {data.get('clinical_status')} | R/B: {data.get('ratio_rb')} | ID: #{data.get('id')}")
    except Exception as e:
        print(f"  -> [HTTP ERROR] Could not reach {backend_url}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate ESP32 GY-9960 sensor node sequence.")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/sensor/readings", help="Target API endpoint URL (default: http://127.0.0.1:5000/api/sensor/readings)")
    parser.add_argument("--cycles", type=int, default=3, help="Number of full cycles to run (0 for infinite, default: 3)")
    args = parser.parse_args()

    print("=================================================================")
    print(" ESP32 Optical Sensor Node (GY-9960) Hardware Simulation")
    print("=================================================================")
    print(f" Target Endpoint : {args.url}")
    print(f" Sequence        : OFF (1033ms) -> BLUE (1033ms) -> GREEN (1033ms) -> WHITE (1033ms) -> Pause (2062ms)")
    print(f" Cycles          : {'Continuous' if args.cycles == 0 else args.cycles}")
    print("=================================================================\n")

    start_time_ms = int(time.time() * 1000)
    cycle = 1
    step_num = 1

    try:
        while True:
            print(f"--- [CYCLE #{cycle}] Starting Illumination Sequence ---")
            for mode in ILLUMINATION_MODES:
                simulate_step(step_num, mode, args.url, start_time_ms)
                step_num += 1
                time.sleep(1.033)

            print(f"--- [CYCLE #{cycle} COMPLETE] Pausing 2.06s before next cycle ---\n")
            if args.cycles > 0 and cycle >= args.cycles:
                break
            cycle += 1
            time.sleep(2.062)

        print("[SUCCESS] Hardware simulation sequence completed successfully.")
    except KeyboardInterrupt:
        print("\n[STOPPED] Simulation interrupted by user.")
