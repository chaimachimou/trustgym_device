import time
import json
import base64
import hashlib
import hmac
import requests

# Your API keys and endpoint details
app_key = '26737313'
app_secret = 'VMCICEDXszmI4z8bYSlm'
url = "http://127.0.0.1:9016/artemis/api/resource/v1/person/single/delete"

# Request body (JSON data)
body = {
    "personId": "19",
    "personCode": "123245",
    "personFamilyName": "Li",
    "personGivenName": "person0",
    "orgIndexCode": "1",
    "gender": 1,
    "phoneNo": "13000110011",
    "remark": "description",
    "email": "person1@qq.com",
    "cards": [
        {
            "cardNo": "123456"
        }
    ],
    "beginTime": "2020-05-26T15:00:00+08:00",
    "endTime": "2030-05-26T15:00:00+08:00",
    "residentRoomNo": 9999,
    "residentFloorNo": 111
}

# Convert body to JSON string
body_json = json.dumps(body)
body_length = len(body_json)

# Current timestamp (seconds since epoch)
timestamp = str(int(time.time()))

string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/single/update"

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
    'userId': 'admin',  # Replace with your actual userId if needed
}

# Print the headers for debugging
print("\nRequest Headers:")
print(json.dumps(headers, indent=4))

# Send the POST request to the server
try:
    response = requests.post(url, headers=headers, json=body)  # Removed 'verify=False' for HTTP

    # Check if the request was successful
    if response.status_code == 200:
        print("\nResponse received:")
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"Error during the request: {e}")
