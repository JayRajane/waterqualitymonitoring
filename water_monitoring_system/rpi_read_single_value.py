import requests
import time
from pymodbus.client import ModbusSerialClient

# Configuration
SERVER_URL = 'http://192.168.1.101:8000'
USERNAME = 'shreni'
PASSWORD = 'shreni@123'
USER_ID = 2

MODBUS_PORT = '/dev/ttyUSB0'  
MODBUS_BAUDRATE = 9600
MODBUS_DEVICE_ID = 1
MODBUS_ADDRESS = 0

# Create a session for HTTP requests
http_session = requests.Session()

def login_to_server():
    """Login to the Django server and get CSRF token"""
    print("Logging in...")
    
    # Get login page to obtain CSRF token
    login_page = http_session.get(f"{SERVER_URL}/accounts/login/")
    csrf_token = http_session.cookies.get('csrftoken')
    
    if not csrf_token:
        print("Could not get CSRF token")
        return False
    
    # Prepare login data
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token
    }
    
    # Attempt login
    login_response = http_session.post(
        f"{SERVER_URL}/accounts/login/",
        data=login_data,
        headers={'Referer': f"{SERVER_URL}/accounts/login/"}
    )
    
    # Check if login was successful
    if login_response.status_code == 200 and 'login' not in login_response.url:
        print("Login successful!")
        return True
    else:
        print("Login failed")
        return False

def read_ph_value():
    """Read pH value from Modbus device"""
    try:
        # Connect to Modbus device
        client = ModbusSerialClient(
            port=MODBUS_PORT,
            baudrate=MODBUS_BAUDRATE,
            timeout=1
        )
        
        if not client.connect():
            print("Could not connect to Modbus device")
            return None
        
        # Read the register
        result = client.read_holding_registers(
            address=MODBUS_ADDRESS,
            count=1,
            slave=MODBUS_DEVICE_ID
        )
        
        if result.isError():
            print("Error reading from Modbus")
            return None
        
        # Convert the value to pH (adjust scaling as needed)
        ph_value = result.registers[0] / 10.0
        return ph_value
        
    except Exception as e:
        print(f"Modbus error: {e}")
        return None
    finally:
        client.close()

def send_ph_data():
    """Send pH data to the server"""
    ph_value = read_ph_value()
    
    if ph_value is None:
        print("No pH data to send")
        return
    
    print(f"Read pH value: {ph_value}")
    
    # Prepare data to send
    data = {
        'user_id': USER_ID,
        'ph': ph_value
    }
    
    # Get CSRF token from session
    csrf_token = http_session.cookies.get('csrftoken')
    
    if not csrf_token:
        print("No CSRF token available")
        return
    
    # Send the data
    try:
        response = http_session.post(
            f"{SERVER_URL}/submit-data/",
            data=data,
            headers={
                'X-CSRFToken': csrf_token,
                'Referer': SERVER_URL
            }
        )
        
        if response.status_code == 200:
            print("Data sent successfully")
        else:
            print(f"Server responded with status: {response.status_code}")
            
    except Exception as e:
        print(f"Error sending data: {e}")

def main():
    """Main program loop"""
    if not login_to_server():
        return
    
    while True:
        send_ph_data()
        time.sleep(5)  # Wait 5 seconds between readings

if __name__ == "__main__":
    main()