import requests
import json
import base64
import hmac
import hashlib
import time
from datetime import datetime, timezone

# Define API credentials 
app_key = "27435223"
app_secret = "J194LCQU62Sl81YSYBkg"
base_url = "http://196.224.39.92/artemis/api/resource/v1/person/advance/personList"

# Generate a timestamp
timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds

# Prepare the body of the request
payload = {
    "pageNo": 1,
    "pageSize": 10,
    "personName": "chaima"  # Replace with the name you want to search
}

# String to sign for API authentication
# This should be based on your specific API requirements
string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/advance/personList"

# Generate the x-ca-signature (HMAC-SHA256)
signature = hmac.new(
    app_secret.encode('utf-8'),
    string_to_sign.encode('utf-8'),
    hashlib.sha256
).digest()

# Base64 encode the signature
signature_base64 = base64.b64encode(signature).decode('utf-8')

# Prepare headers for the request
headers = {
    'x-ca-key': app_key,
    'x-ca-signature': signature_base64,
    'Content-Type': 'application/json',
    'Timestamp': timestamp,
    'userId': 'admin',  # Replace with your actual userId if needed
}

# Send the POST request
try:
    response = requests.post(base_url, headers=headers, json=payload, verify=False)
    response.raise_for_status()  # Check for HTTP errors

    # Assuming the response is in JSON format, process it accordingly
    response_data = response.json()

    # Check for success in the response data
    if response_data.get('code') == '0' and response_data.get('data', {}).get('list'):
        # Extract person data from the response
        people = response_data['data']['list']
        
        # Extract 'endTime' and compare it with the current time
        for person in people:
            end_time = person.get('endTime')
            if end_time:
                # Convert endTime to a datetime object (adjusted format)
                end_time_datetime = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S%z")

                # Get the current time as a timezone-aware datetime object (UTC)
                current_time = datetime.now(timezone.utc)

                # Compare endTime with current time and output only the boolean result
                print(end_time_datetime > current_time)
            else:
                print(False)  # If no endTime is found, return False

except requests.exceptions.RequestException as e:
    print(False)  # If an error occurs, return False
