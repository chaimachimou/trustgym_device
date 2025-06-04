import time
import json
import base64
import hashlib
import hmac
import requests

# Your API keys and endpoint details 
app_key = '27435223' 
app_secret = 'J194LCQU62Sl81YSYBkg' 
url = 'http://196.224.39.92/artemis/api/eventService/v1/eventSubscriptionByEventTypes'  # Corrected URL

# prepare the request body (event subscription)
body = {
    "eventTypes": [198194,197127,196893],  # List of event types
    "eventDest": "http://192.168.1.30:544/eventRcv"  # The event destination URL
}


# Convert body to JSON string
body_json = json.dumps(body)
body_length = len(body_json)

# Current timestamp (seconds since epoch)
timestamp = str(int(time.time()))

# Prepare the String to Sign (Correct format with Content-Type and the right request path)
string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/eventService/v1/eventSubscriptionByEventTypes"  # Corrected path 

# Print the string to sign for debugging
print("String to Sign:")
print(string_to_sign)

# Generate the x-ca-signature (HMAC-SHA256)
signature = hmac.new(
    app_secret.encode('utf-8'),
    string_to_sign.encode('utf-8'),
    hashlib.sha256
).digest()

# Base64 encode the signature
signature_base64 = base64.b64encode(signature).decode('utf-8')

# Print the generated signature for debugging
print("\nGenerated Signature (Base64):")
print(signature_base64)

# Prepare the headers for the request
headers = {
    'x-ca-key': app_key,  # Ensure using the correct case for the key
    'x-ca-signature': signature_base64,  # Correct header: x-ca-signature in lowercase
    'Content-Type': 'application/json',
    'Timestamp': timestamp,
}

# Print the headers for debugging
print("\nRequest Headers:")
print(json.dumps(headers, indent=4))

# Send the POST request to the server
try:
    response = requests.post(url, headers=headers, json=body)

    # Check if the request was successful
    if response.status_code == 200:
        print("\nResponse received:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error during the request: {e}")
