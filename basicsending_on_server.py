#!/usr/bin/env python3
import requests
from pymodbus.client import ModbusSerialClient
import time
import json

# Configuration
USER_ID = 4
PH_DEVICE_ID = 1
INTERVAL = 5  # seconds between readings

# Setup pH sensor connection
ph_client = ModbusSerialClient(
    port='/dev/ttyUSB0',
    baudrate=9600,
    timeout=5,
    parity='N',
    stopbits=1,
    bytesize=8
)

def read_ph():
    """Read pH value from sensor"""
    try:
        response = ph_client.read_holding_registers(address=0, count=1, slave=PH_DEVICE_ID)
        if not response.isError():
            raw_value = response.registers[0]
            ph_value = round(raw_value / 100, 2)
            print(f"pH Reading: {ph_value}")
            return ph_value
        else:
            print("Error reading pH sensor")
            return None
    except Exception as e:
        print(f"pH read error: {e}")
        return None

def send_data(ph_value):
    """Send pH data to server"""
    try:
        data = {'user_id': USER_ID, 'ph': ph_value}
        response = requests.post('http://192.168.1.102:8000/submit-data/', json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✓ Data sent successfully!")
                return True
        print("✗ Failed to send data")
        return False
    except Exception as e:
        print(f"Send error: {e}")
        return False

def main():
    # Connect to pH sensor
    print("Connecting to pH sensor...")
    if not ph_client.connect():
        print("Failed to connect to pH sensor!")
        return
    
    print("pH sensor connected. Starting readings...")
    
    try:
        while True:
            # Read pH value
            ph_value = read_ph()
            
            # Send data if valid
            if ph_value is not None and 0 <= ph_value <= 14:
                send_data(ph_value)
            else:
                print("Invalid pH reading, skipping...")
            
            # Wait before next reading
            print(f"Waiting {INTERVAL} seconds...\n")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        ph_client.close()
        print("pH sensor disconnected.")

if __name__ == "__main__":
    main()