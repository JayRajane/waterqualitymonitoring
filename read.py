from pymodbus.client import ModbusSerialClient
import time
import requests
import json

# Server configuration
SERVER_URL = "https://www.impulseengineers.com/app/record_new_cod_bod_tss_data/"
USER_ID = 1  # Fixed user ID as specified
LAPTOP_IP = "192.168.x.x"  # Replace with your laptop's IP address
CALIBRATION_STATUS_URL = f"http://192.168.1.103:5000/api/calibration_status"

# Device configuration
DEVICE_ID = 1  # All parameters use the same device ID
# Define different addresses for each sensor (adjust as per your Modbus device)
SENSOR_ADDRESSES = {
    'COD': 0,
    'BOD': 0,
    'TSS': 0,
    'pH': 0,
    'Flow': 1,
    'Total_Flow': 1
}
PORT = '/dev/ttyUSB0'

def initialize_client(port):
    """Initialize Modbus RTU client with common settings"""
    return ModbusSerialClient(
        method='rtu',
        port=port,
        baudrate=9600,
        parity='N',
        stopbits=1,
        bytesize=8,
        timeout=2.0
    )

def read_holding_register(client, address, device_id):
    """Read value from holding register (single register)"""
    try:
        response = client.read_holding_registers(address=address, count=1, slave=device_id)
        if response.isError():
            print(f"Error reading holding register at address {address}: {response}")
            return None
        return response.registers[0] / 10  # Scale value (e.g., 723 → 7.23)
    except Exception as e:
        print(f"Error reading holding register at address {address}: {e}")
        return None

def read_all_sensors(client):
    """Read all sensor values from their respective addresses"""
    sensor_data = {}

    for sensor, address in SENSOR_ADDRESSES.items():
        value = read_holding_register(client, address, DEVICE_ID)
        sensor_data[sensor] = round(value, 2) if value is not None else None

    return sensor_data

def check_calibration_status():
    """Check if calibration mode is active by querying the Flask server"""
    try:
        response = requests.get(CALIBRATION_STATUS_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("calibration_active", False)
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error checking calibration status: {e}")
        return False  # Assume normal mode if server is unreachable

def send_data_to_server(sensor_data):
    """Send sensor data to the server"""
    try:
        payload = {
            "user_id": USER_ID,
            "ph": sensor_data.get('pH'),
            "flow_rate": sensor_data.get('Flow'),
            "flow_total": sensor_data.get('Total_Flow'),
            "cod": sensor_data.get('COD'),
            "bod": sensor_data.get('BOD'),
            "tss": sensor_data.get('TSS'),
            "record": True
        }

        payload = {k: v for k, v in payload.items() if v is not None}

        if len(payload) > 2:  # More than just user_id and record
            headers = {'Content-Type': 'application/json'}
            response = requests.post(SERVER_URL, json=payload, headers=headers, timeout=10)

            if response.status_code == 200:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully sent sensor data")
                print(f"  Payload: {json.dumps(payload, indent=2)}")
                return True
            else:
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Server response error: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
        else:
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Insufficient sensor data to send")
            return False
    except requests.exceptions.RequestException as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Network error sending data to server: {e}")
        return False
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ✗ Error sending data to server: {e}")
        return False

def main():
    """Main function to continuously read and send sensor data"""
    client = initialize_client(PORT)

    if not client.connect():
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Failed to connect to Modbus device.")
        return

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Connected to Modbus device successfully!")
    print("Starting sensor data collection...\n")

    try:
        while True:
            # Check calibration status
            if check_calibration_status():
                print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] In calibration mode, skipping sensor data send")
                time.sleep(5)
                continue

            sensor_data = read_all_sensors(client)

            if sensor_data:
                print("=" * 50)
                print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("-" * 50)

                for sensor, value in sensor_data.items():
                    if value is not None:
                        if sensor in ['COD', 'BOD', 'TSS']:
                            print(f"{sensor}: {value} mg/L")
                        elif sensor == 'pH':
                            print(f"{sensor}: {value}")
                        elif sensor == 'Total_Flow':
                            print(f"{sensor}: {value} L")
                        elif sensor == 'Flow':
                            print(f"{sensor}: {value} L/min")

                print("-" * 50)

                send_data_to_server(sensor_data)

                print("=" * 50)

            time.sleep(5)  # Reading interval

    except KeyboardInterrupt:
        print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Stopping sensor data collection...")
    finally:
        client.close()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Modbus connection closed.")

if __name__ == "__main__":
    main()