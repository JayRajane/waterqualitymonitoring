import requests
import time
import re
import random
from datetime import datetime

# Django server URL
BASE_URL = 'http://127.0.0.1:8000'

# Login credentials
LOGIN_URL = f'{BASE_URL}/accounts/login/'
USERNAME = 'blisspharama'
PASSWORD = 'blisspharama@123'

# API endpoint after login
API_URL = f'{BASE_URL}/api/water-quality/submit_data/'

# Create a session object
session = requests.Session()

def login():
    print("Logging in...")
    
    response = session.get(LOGIN_URL)
    if response.status_code != 200:
        print("Failed to load login page!")
        exit()
    
    match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
    if match:
        csrf_token = match.group(1)
    else:
        print("CSRF token not found!")
        exit()
    
    print(f"CSRF Token fetched: {csrf_token}")

    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token,
    }
    
    headers = {
        'Referer': LOGIN_URL,
        'Content-Type': 'application/x-www-form-urlencoded',
    }

    response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    
    if response.status_code == 200 and 'login' not in response.url:
        print("Login successful!")
    else:
        print("Login failed. Check credentials or server!")
        print(response.text)
        exit()

def generate_data():
    """Generates random flow data with the current timestamp."""
    return {
        "user": 2,
        "timestamp": datetime.now().isoformat(),  # Current timestamp
        "flow1": round(random.uniform(10, 100), 2),  # Random float between 10 and 100
        "flow2": round(random.uniform(10, 100), 2),
        "flow3": round(random.uniform(10, 100), 2),
    }

def send_data():
    """Sends the data to the server."""
    data = generate_data()
    print(f"Sending data: {data}")
    
    csrf_token = session.cookies.get('csrftoken')
    if not csrf_token:
        print("CSRF token is missing! Can't send data.")
        return

    headers = {
        'X-CSRFToken': csrf_token,
        'Content-Type': 'application/json',
    }

    try:
        response = session.post(API_URL, json=data, headers=headers)
        print(f"Status Code: {response.status_code}")
        try:
            print("Response:", response.json())
        except requests.exceptions.JSONDecodeError:
            print("Server replied, but not JSON:", response.text)
    except Exception as e:
        print("Error while sending:", str(e))

def start_sending_data():
    login()
    while True:
        send_data()
        time.sleep(5)

if __name__ == "__main__":
    start_sending_data()
