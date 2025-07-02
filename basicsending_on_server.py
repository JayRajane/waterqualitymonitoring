#!/usr/bin/env python3
import requests
import time
import json
import random

# Configuration
USER_ID = 4
INTERVAL = 5  # seconds between readings
FLOW4_TOTAL = 346788  # starting value for flow4_total

def generate_flow4_data():
    """Generate random flow4 value and update flow4_total incrementally"""
    global FLOW4_TOTAL
    flow4 = round(random.uniform(0.5, 5.0), 2)  # Random flow4 value between 0.5 and 5.0
    
    # Increment flow4_total by a random amount (1 to 10) to ensure it always increases
    increment = random.randint(1, 10)
    FLOW4_TOTAL += increment
    
    print(f"Flow4: {flow4}, Flow4 Total: {FLOW4_TOTAL} (increased by {increment})")
    return flow4, FLOW4_TOTAL

def send_data(flow4, flow4_total):
    """Send flow data to server"""
    try:
        data = {
            'user_id': USER_ID,
            'flow4': flow4,
            'flow4_total': flow4_total
        }
        response = requests.post('http://127.0.0.1:8000/submit-data/', json=data, timeout=10)
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
    print("Starting flow4 data logger...")
    print(f"Initial Flow4 Total: {FLOW4_TOTAL}")
    
    try:
        while True:
            # Generate flow4 data
            flow4, flow4_total = generate_flow4_data()
            
            # Send data
            send_data(flow4, flow4_total)
            
            # Wait before next reading
            print(f"Waiting {INTERVAL} seconds...\n")
            time.sleep(INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        print("Flow4 data logger stopped.")

if __name__ == "__main__":
    main()