import requests
import random
import time
import re

# Django server URL
BASE_URL = 'http://127.0.0.1:8000'

# Login credentials
LOGIN_URL = f'{BASE_URL}/accounts/login/'
USERNAME = 'abhishek'
PASSWORD = 'abhishek@123'

# API endpoint after login
API_URL = f'{BASE_URL}/api/water-quality/submit_data/'

# Create a session object (to maintain cookies, csrf)
session = requests.Session()

def login():
    print("Logging in...")
    
    # 1. GET the login page first to fetch CSRF token
    response = session.get(LOGIN_URL)
    if response.status_code != 200:
        print("Failed to load login page!")
        exit()
    
    # 2. Extract CSRF token from the login page
    csrf_token = None
    match = re.search(r'name="csrfmiddlewaretoken" value="(.+?)"', response.text)
    if match:
        csrf_token = match.group(1)
    else:
        print("CSRF token not found!")
        exit()
    
    print(f"CSRF Token fetched: {csrf_token}")

    # 3. Now post login data along with csrf token
    login_data = {
        'username': USERNAME,
        'password': PASSWORD,
        'csrfmiddlewaretoken': csrf_token,
    }
    
    headers = {
        'Referer': LOGIN_URL,  # Important for CSRF protection
        'Content-Type': 'application/x-www-form-urlencoded',  # Tells Django it's a normal form post
    }

    response = session.post(LOGIN_URL, data=login_data, headers=headers, allow_redirects=True)
    
    # Check for successful login (redirection to the correct page)
    if response.status_code == 200 and 'login' not in response.url:
        print("Login successful!")
    else:
        print("Login failed. Check credentials or server!")
        print(response.text)
        exit()

def generate_random_data():
    """Generates random environmental sensor data."""
    return {
        "user": 5,  # Use the correct user ID here
        "ph": round(random.uniform(6.5, 8.5), 2),
        "flow1": round(random.uniform(10, 100), 2),
        "flow2": round(random.uniform(10, 100), 2),
        "flow3": round(random.uniform(10, 100), 2),
        "cod": random.randint(20, 300),
        "bod": random.randint(5, 80),
        "tss": random.randint(10, 200),
    }

def send_data():
    """Sends random sensor data to the server."""
    data = generate_random_data()
    print(f"Sending data: {data}")
    
    # Get CSRF token from session cookies
    csrf_token = session.cookies.get('csrftoken')

    # Check if CSRF token is available
    if not csrf_token:
        print("CSRF token is missing! Can't send data.")
        return

    # Include CSRF token in headers for POST request
    headers = {
        'X-CSRFToken': csrf_token,  # Pass CSRF token here
        'Content-Type': 'application/json',  # Content type for JSON
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
        time.sleep(5)  # Wait 5 seconds before sending again

if __name__ == "__main__":
    start_sending_data()
