import base64
import hashlib
import hmac
import json
import time
import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET

# Your API keys and endpoint details
app_key = '27435223'
app_secret = 'J194LCQU62Sl81YSYBkg'
url_person_add = "http://127.0.0.1:9016/artemis/api/resource/v1/person/single/add"  # Your provided API endpoint for adding person
url_privilege_group_add = "http://127.0.0.1:9016/artemis/api/acs/v1/privilege/group/single/addPersons"  # Privilege group API

# Device information for fingerprint capture
ip_address = "192.168.1.50"  # Your device's IP address
port = "80"  # The port number
username = "admin"  # Update with your username
password = "Admin123"  # Update with your password

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

# Function to add a person with fingerprint data to the system and return the person's ID
def add_person_with_fingerprint(fingerprint_data):
    if not fingerprint_data:
        print("No fingerprint data to add.")
        return None

    # Convert fingerprint to Hexadecimal format
    fingerprint_hex = convert_to_hex(fingerprint_data)

    # Generate a unique personCode based on the current timestamp
    person_code = str(int(time.time()))  # Generate unique person code using current timestamp

    # Use fingerprint_hex for the fingerprint data field in the API request
    body = {
        "personCode": person_code,  # Use the generated unique person code
        "personFamilyName": "try",
        "gender": 2,
        "orgIndexCode": "1",
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
        'userId': 'admin',  # You can replace 'admin' with the actual username if needed
    }

    # Send the POST request to the server to add the person
    try:
        response = requests.post(url_person_add, headers=headers, json=body)
        
        # Debugging: print the full response to see what it contains
        print("\nFull Response:")
        print(response.text)  # Print the raw response text

        if response.status_code == 200:
            print("\nPerson added successfully.")
            print(json.dumps(response.json(), indent=4))

            # Check if the response contains the person ID
            response_data = response.json()

            # Debugging: print the full response JSON to examine its structure
            print(f"Response Data: {json.dumps(response_data, indent=4)}")
            
            if response_data.get("data"):
                person_id = response_data.get("data")
                
                # Ensure the person_id is a string and pad it to 64 characters if necessary
                person_id_str = str(person_id).ljust(64)  # Pad to 64 characters
                
                print(f"Processed Person ID: {person_id_str}")
                print(f"Length of Processed Person ID: {len(person_id_str)}")  # Debugging: Print the length
                return person_id_str  # Return as padded string
            else:
                print("No person ID returned. The person may already exist.")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error during the request: {e}")
        return None

# Function to add person data to a privilege group
def add_person_to_privilege_group(person_id):
    if not person_id:
        print("No person ID to add to privilege group.")
        return

    body = {
        "privilegeGroupId": "1",  # Update the group ID as needed
        "type": 1,  # Assuming 1 is for adding a person
        "list": [
            {
                "id": person_id
            }
        ]
    }

    body_json = json.dumps(body)
    body_length = len(body_json)

    # Current timestamp (seconds since epoch)
    timestamp = str(int(time.time()))

    # Prepare the string to sign (exclude the body in the string-to-sign)
    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/acs/v1/privilege/group/single/addPersons"

    # Debugging: print the string to sign before generating the signature
    print("String to sign for privilege group API:")
    print(string_to_sign)  # Debugging: print the string to sign

    # Generate the signature using HMAC-SHA256
    signature = hmac.new(
        app_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()

    # Base64 encode the signature
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    # Debugging: print the generated signature
    print("Generated Signature Base64:")
    print(signature_base64)

    # Prepare headers for the request
    headers = {
        'x-ca-key': app_key,
        'x-ca-signature': signature_base64,
        'Content-Type': 'application/json',
        'Timestamp': timestamp,
        'userId': 'admin',  # You can replace 'admin' with the actual username if needed
    }

    # Send the POST request to add the person to the privilege group
    try:
        response = requests.post(url_privilege_group_add, headers=headers, json=body)

        if response.status_code == 200:
            print(f"Person {person_id} added to the privilege group successfully.")
        else:
            print(f"Failed to add person to privilege group. Status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during the request: {e}")

def main():
    # Capture fingerprint data from the device (You should replace this with actual fingerprint data)
    fingerprint_data = capture_fingerprint(finger_number=1)  # Replace with the desired finger number
    
    if fingerprint_data:
        # Parse the fingerprint response and get the base64 encoded fingerprint data
        fingerprint_data = parse_response(fingerprint_data)

        if fingerprint_data:
            # Add person with fingerprint data and get the person ID
            person_id = add_person_with_fingerprint(fingerprint_data)

            if person_id:
                # Assign the person to a privilege group using the extracted person ID
                add_person_to_privilege_group(person_id)

if __name__ == "__main__":
    main()
