#!/usr/bin/env python
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
import json
import threading
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Server configuration
DATA_SOURCE_URL = "https://impulseengineers.com/app/get_cod_bod_tss_spm_data/1/"
SUBMIT_URL = "https://www.impulseengineers.com/app/record_new_cod_bod_tss_data/"
USER_ID = 1

# In-memory storage for calibration data
calibration_data = None

def background_sender():
    """Background thread to send calibrated data every 5 seconds"""
    while True:
        if calibration_data is not None:
            try:
                headers = {'Content-Type': 'application/json'}
                response = requests.post(SUBMIT_URL, json=calibration_data, headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully sent calibrated data")
                    print(f"  Payload: {json.dumps(calibration_data, indent=2)}")
                else:
                    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Server response error for calibrated data: {response.status_code}")
                    print(f"  Response: {response.text}")
            except Exception as e:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error sending calibrated data: {e}")
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No calibration data, skipping send")
        time.sleep(5)

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/api/data')
def get_data():
    """Proxy to fetch data from the remote server"""
    try:
        response = requests.get(DATA_SOURCE_URL, headers={'Accept': 'application/json'}, timeout=5)
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching data: {e}")
        return jsonify({"status": "unavailable", "message": "Server unavailable, using last fetched data or 00"})

@app.route('/api/calibrate', methods=['POST'])
def submit_calibration():
    """Handle calibration submission and store in memory"""
    global calibration_data
    try:
        data = request.get_json()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Incoming calibration data: {json.dumps(data, indent=2)}")
        
        # Map frontend field names to server-expected names
        calibration_data = {
            "user_id": USER_ID,
            "ph": data.get("ph", None),
            "cod": data.get("cod", None),
            "bod": data.get("bod", None),
            "tss": data.get("tss", None),
            "flow_rate": data.get("flow", None),
            "daily_flow": data.get("daily_flow", None),
            "record": True
        }
        
        # Remove None values
        calibration_data = {k: v for k, v in calibration_data.items() if v is not None}
        
        return jsonify({"status": "success", "message": "Calibration data saved and will be sent continuously"})
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error submitting calibration data: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reset', methods=['POST'])
def reset_calibration():
    """Reset calibration by clearing in-memory data"""
    global calibration_data
    try:
        if calibration_data is not None:
            calibration_data = None
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Calibration data cleared")
            return jsonify({"status": "success", "message": "Calibration reset successful"})
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] No calibration data to reset")
            return jsonify({"status": "success", "message": "No calibration to reset"})
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error resetting calibration: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/calibration_status')
def get_calibration_status():
    """Return whether calibration mode is active and the calibration data"""
    return jsonify({
        "calibration_active": calibration_data is not None,
        "calibration_data": calibration_data
    })

if __name__ == '__main__':
    sender_thread = threading.Thread(target=background_sender, daemon=True)
    sender_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=True)  