import requests
import time
import re
from pymodbus.client import ModbusSerialClient

# Django server settings
BASE_URL = 'http://192.168.1.101:8000'
LOGIN_URL = f'{BASE_URL}/accounts/login/'
SUBMIT_URL = f'{BASE_URL}/submit-data/'
USERNAME = 'shreni'
PASSWORD = 'shreni@123'
USER_ID = 2

# Modbus connection settings
PORT = '/dev/ttyUSB0' 
BAUDRATE = 9600

# Modbus read parameters (separated)
DEVICE_ID = 1
ADDRESS = 0
COUNT = 1

# Create a persistent session
session = requests.Session()


def get_csrf_token():
    """Get CSRF token from login page."""
    try:
        response = session.get(LOGIN_URL)
        match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
        return match.group(1) if match else None
    except Exception as e:
        print("Error fetching CSRF token:", e)
        return None


def login():
    """Login to Django and keep session active."""
    print("Logging in...")
    csrf_token = get_csrf_token()
    if not csrf_token:
        print("CSRF token not found.")
        return False

    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    headers = {
        'Referer': LOGIN_URL
    }

    try:
        response = session.post(LOGIN_URL, data=data, headers=headers)
        if response.status_code == 200 and 'login' not in response.url:
            print("Login successful.")
            return True
        else:
            print(f"Login failed. Status: {response.status_code}, URL: {response.url}")
            return False
    except Exception as e:
        print("Login error:", e)
        return False


def read_ph_from_modbus():
    """Read pH value from Modbus device."""
    client = ModbusSerialClient(
        port=PORT,
        baudrate=BAUDRATE,
        timeout=1,
        parity='N',
        stopbits=1,
        bytesize=8
    )

    if not client.connect():
        print("Failed to connect to Modbus device.")
        return None

    try:
        result = client.read_holding_registers(address=ADDRESS, count=COUNT, slave=DEVICE_ID)
        if result.isError():
            print("Modbus read error.")
            return None

        ph = result.registers[0] / 10.0  # Adjust if scaling changes
        return {'user_id': USER_ID, 'ph': ph}

    except Exception as e:
        print("Modbus exception:", e)
        return None
    finally:
        client.close()


def send_data():
    """Send data to Django server."""
    data = read_ph_from_modbus()
    if not data:
        print("No data read.")
        return

    csrf_token = session.cookies.get('csrftoken')
    if not csrf_token:
        print("Missing CSRF token.")
        return

    headers = {
        'X-CSRFToken': csrf_token,
        'Referer': BASE_URL
    }

    try:
        response = session.post(SUBMIT_URL, data=data, headers=headers)
        print(f"Response: {response.status_code}")

        try:
            res_json = response.json()
            if res_json.get('success'):
                print("Data submitted successfully.")
            else:
                print("Server error:", res_json.get('error', 'Unknown error'))
        except Exception:
            print("Non-JSON response:", response.text)

    except Exception as e:
        print("Error sending data:", e)


def start():
    """Main loop: login once, then send data every 5 seconds."""
    if not login():
        print("Login failed. Exiting.")
        return

    while True:
        send_data()
        time.sleep(5)  # Adjust interval if needed


if __name__ == "__main__":
    start()
