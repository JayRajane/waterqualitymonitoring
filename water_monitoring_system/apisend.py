import requests
import random
import time
from datetime import datetime

# API endpoint and login URL
BASE_URL = "http://192.168.1.102:8000"
LOGIN_URL = f"{BASE_URL}/accounts/login/"
SUBMIT_DATA_URL = f"{BASE_URL}/submit-data/"

# User credentials
USERNAME = "abhi"
PASSWORD = "abhi@123"
USER_ID = 2

# Interval between data submissions (in seconds)
SUBMISSION_INTERVAL = 5  # Adjust as needed

# Create a session to maintain cookies
session = requests.Session()

def login():
    """Log in to the server and return the CSRF token."""
    try:
        # Get CSRF token
        response = session.get(BASE_URL, timeout=10)
        if 'csrftoken' not in session.cookies:
            print("Failed to retrieve CSRF token from server.")
            return None
        csrf_token = session.cookies.get('csrftoken')
        print("CSRF Token retrieved:", csrf_token)

        # Log in
        login_data = {
            'username': USERNAME,
            'password': PASSWORD,
            'csrfmiddlewaretoken': csrf_token
        }
        headers = {
            'Referer': LOGIN_URL,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        login_response = session.post(LOGIN_URL, data=login_data, headers=headers, timeout=10)
        if login_response.status_code == 200:
            print("Login successful.")
            # Refresh CSRF token after login
            response = session.get(BASE_URL, timeout=10)
            csrf_token = session.cookies.get('csrftoken')
            print("CSRF Token after login:", csrf_token)
            return csrf_token
        else:
            print("Login failed. Status code:", login_response.status_code, "Response:", login_response.text)
            return None
    except requests.RequestException as e:
        print("Error during login:", str(e))
        return None

def submit_data(csrf_token):
    """Submit random flow data to the server."""
    flow_data = {
        'user_id': USER_ID,
        'flow1': round(random.uniform(0, 100), 2),  # Random flow1 value (0 to 100 L/min)
        'flow2': round(random.uniform(0, 100), 2),  # Random flow2 value (0 to 100 L/min)
        'flow3': round(random.uniform(0, 100), 2),  # Random flow3 value (0 to 100 L/min)
        'csrfmiddlewaretoken': csrf_token
    }
    print(f"{datetime.now()}: Data to submit:", flow_data)
    
    submit_headers = {
        'Referer': SUBMIT_DATA_URL,
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-CSRFToken': csrf_token
    }
    try:
        submit_response = session.post(SUBMIT_DATA_URL, data=flow_data, headers=submit_headers, timeout=10)
        if submit_response.status_code == 200:
            try:
                response_json = submit_response.json()
                if response_json.get('success'):
                    print(f"{datetime.now()}: Data submitted successfully:", flow_data)
                else:
                    print(f"{datetime.now()}: Error submitting data:", response_json.get('error'))
            except ValueError:
                print(f"{datetime.now()}: Invalid JSON response:", submit_response.text)
        else:
            print(f"{datetime.now()}: Failed to submit data. Status code:", submit_response.status_code, "Response:", submit_response.text)
            if submit_response.status_code == 403:
                print(f"{datetime.now()}: 403 Forbidden - Likely CSRF or session issue. Attempting to re-login.")
                return False
    except requests.RequestException as e:
        print(f"{datetime.now()}: Error submitting data:", str(e))
    return True

def main():
    # Initial login
    csrf_token = login()
    if not csrf_token:
        print("Exiting due to login failure.")
        return

    # Counter for session refresh (every 25 minutes to stay within 30-minute session timeout)
    session_refresh_interval = 25 * 60  # 25 minutes in seconds
    last_refresh = time.time()

    while True:
        # Check if session needs refresh
        if time.time() - last_refresh > session_refresh_interval:
            print(f"{datetime.now()}: Session nearing timeout. Refreshing login.")
            csrf_token = login()
            if not csrf_token:
                print(f"{datetime.now()}: Re-login failed. Retrying in 60 seconds.")
                time.sleep(60)
                continue
            last_refresh = time.time()

        # Submit data
        success = submit_data(csrf_token)
        if not success:
            print(f"{datetime.now()}: Re-login required due to submission failure.")
            csrf_token = login()
            if not csrf_token:
                print(f"{datetime.now()}: Re-login failed. Retrying in 60 seconds.")
                time.sleep(60)
                continue
            last_refresh = time.time()

        # Wait before next submission
        time.sleep(SUBMISSION_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Script stopped by user.")