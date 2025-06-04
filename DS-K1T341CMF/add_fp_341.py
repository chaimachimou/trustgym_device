import base64
import hashlib
import hmac
import json
import requests
import time
import xml.etree.ElementTree as ET
from requests.auth import HTTPDigestAuth

# Your API keys and endpoint details
app_key = '26737313'  # Your provided API key
app_secret = 'VMCICEDXszmI4z8bYSlm'  # Your provided API secret
url = "http://196.224.39.92/artemis/api/resource/v1/person/single/add"  # Your provided API endpoint

# Device information for fingerprint capture
ip_address = "192.168.1.32"  # Your device's IP address
port = "80"                   # The port number
username = "admin"            # Update with your username
password = "Admin123"         # Update with your password 

# Function to capture fingerprint
def capture_fingerprint(finger_number):
    capture_url = f"http://{ip_address}:{port}/ISAPI/AccessControl/CaptureFingerPrint"
    
    # XML request body for capturing fingerprints
    xml_payload = f"""<CaptureFingerPrintCond version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
                        <fingerNo>{finger_number}</fingerNo>
                     </CaptureFingerPrintCond>"""
    
    headers = {'Content-Type': 'application/xml'}
    response = requests.post(capture_url, data=xml_payload, headers=headers, auth=HTTPDigestAuth(username, password))
    
    if response.status_code == 200:
        print("Fingerprint capture initiated successfully.")
        return response.content  # Return binary fingerprint data
    else:
        print(f"Failed to initiate fingerprint capture. Status code: {response.status_code}")
        print(response.content.decode())
        return None

# Function to parse the response and extract fingerprint data
def parse_response(response_content):
    try:
        print("\nRaw XML Response:")
        print(response_content.decode())  # Print the raw XML response
        
        root = ET.fromstring(response_content)
        
        # Define the namespace
        namespace = {'ns': 'http://www.isapi.org/ver20/XMLSchema'}
        
        # Safely extract fingerprint data using the namespace
        finger_data_elem = root.find('.//ns:fingerData', namespace)
        
        if finger_data_elem is not None:
            finger_data = finger_data_elem.text
            print(f"Extracted Fingerprint Data: {finger_data}")  # Debugging: print the raw fingerprint data
            return finger_data
        else:
            print("No fingerprint data found.")
            return None
        
    except ET.ParseError as e:
        print(f"Failed to parse response: {e}")
        return None

# Function to convert fingerprint data to Hexadecimal
def convert_to_hex(fingerprint_data):
    # Convert the fingerprint data (Base64 string) to its raw binary representation
    fingerprint_binary = base64.b64decode(fingerprint_data)
    
    # Convert the binary data to a hexadecimal string
    fingerprint_hex = fingerprint_binary.hex().upper()
    
    return fingerprint_hex

# Function to add person data along with fingerprint to the system
def add_person_with_fingerprint(fingerprint_data):
    if not fingerprint_data:
        print("No fingerprint data to add.")
        return

    # Convert fingerprint to Hexadecimal format
    fingerprint_hex = convert_to_hex(fingerprint_data)

    # Use fingerprint_hex for the fingerprint data field in the API request
    body = {
        "personCode": "12222",
        "personFamilyName": "try",
        "gender": 2,
        "orgIndexCode": "1",
        "phoneNo": "130010011",
        "email": "perso@qq.com",
        "fingerPrint": [
            {
                "fingerPrintIndexCode": "4",
                "fingerPrintName": "fringe_pringt_01",
                "fingerPrintData": fingerprint_hex  # Send Hex data here
            }
        ],
        "beginTime": "2020-05-26T15:00:00+08:00",
        "endTime": "2030-05-26T15:00:00+08:00"
    }

    # Convert body to JSON string
    body_json = json.dumps(body)
    body_length = len(body_json)

    # Current timestamp (seconds since epoch)
    timestamp = str(int(time.time()))

    # String to sign for API authentication
    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/single/add"

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
        'userId': 'admin',
    }

    # Send the POST request to the server
    try:
        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            print("\nResponse received:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during the request: {e}")

def main():
    # Capture fingerprint data from the device
    fingerprint_data = capture_fingerprint(finger_number=1)
    
    if fingerprint_data:
        # Parse the response to extract the fingerprint data
        extracted_fingerprint_data = parse_response(fingerprint_data)
        
        # Add person with the fingerprint data to the system
        add_person_with_fingerprint(extracted_fingerprint_data)

if __name__ == "__main__":
    main()
