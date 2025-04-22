import base64
import hashlib
import hmac
import json
import requests
import time
import xml.etree.ElementTree as ET
from requests.auth import HTTPDigestAuth
from email.parser import BytesParser
from email import policy

# API credentials and URLs
app_key = '26737313' 
app_secret = 'VMCICEDXszmI4z8bYSlm'
url_person_add = "http://127.0.0.1:9016/artemis/api/resource/v1/person/single/add"  # API endpoint for adding person
url_privilege_group_add = "http://127.0.0.1:9016/artemis/api/acs/v1/privilege/group/single/addPersons"  # API endpoint for adding to privilege group

# Device information 
ip_address = "192.168.1.97"   
port = "80"                   
username = "admin"           
password = "Admin123"         

# Function to capture face data with retry logic
def capture_face_data_with_retry(max_retries=5, delay=2):
    url = f"http://{ip_address}:{port}/ISAPI/AccessControl/CaptureFaceData"
    
    # XML request body for capturing face data
    payload = """
    <CaptureFaceDataCond version="2.0" xmlns="http://www.isapi.org/ver20/XMLSchema">
        <captureInfrared>true</captureInfrared>  <!-- Collect infrared data -->
        <dataType>binary</dataType>              <!-- Collect face data as binary -->
    </CaptureFaceDataCond>
    """
    
    headers = {
        "Content-Type": "application/xml",
    }

    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1} of {max_retries} to capture face data...")
        response = requests.post(url, data=payload, headers=headers, auth=HTTPDigestAuth(username, password))

        if response.status_code == 200:
            print("Face data capture request sent successfully.")
            
            # Check the response's content type
            content_type = response.headers.get('Content-Type', ' ')
            print("Response Content-Type:", content_type)

            if 'multipart' in content_type:
                # Handle multipart response, likely containing image data or face data as binary
                try:
                    # Parse the multipart response
                    msg = BytesParser(policy=policy.default).parsebytes(response.content)
                    # Extract the part containing face data (binary image)
                    for part in msg.iter_parts():
                        if part.get_content_type() == 'image/jpeg':  # Assuming the face data is an image
                            face_data_binary = part.get_payload(decode=True)  # Decode the binary face data
                            face_data_base64 = base64.b64encode(face_data_binary).decode('utf-8')  # Re-encode as base64 string
                            print(f"Base64 Encoded Face Data: {face_data_base64}")
                            return face_data_base64
                except Exception as e:
                    print(f"Error parsing multipart response: {e}")
                    return None

            else:
                try:
                    # Try parsing as XML if it's not multipart
                    root = ET.fromstring(response.content)
                    face_data_element = root.find(".//faceData")
                    if face_data_element is not None:
                        face_data_binary = base64.b64decode(face_data_element.text)
                        face_data_base64 = base64.b64encode(face_data_binary).decode('utf-8')
                        print(f"Base64 Encoded Face Data: {face_data_base64}")
                        return face_data_base64
                    else:
                        print("Face data not found in the response.")
                        return None
                except ET.ParseError as e:
                    print(f"Error parsing XML response: {e}")
                    print("Raw response content:", response.content)
                    return None
        else:
            print(f"Failed to send face data capture request. Status code: {response.status_code}")
            print("Response content:", response.text)
        
        # If the device is busy, wait and try again
        if "Device Busy" in response.text:
            print("Device is busy. Retrying...")
            time.sleep(delay)
    
    print("Maximum retries reached. Face data capture failed.")
    return None

# Function to add person data with only face data to the system
def add_person_with_face(face_data):
    if not face_data:
        print("No face data to add.")
        return

    face_base64 = face_data
    
    # Prepare body for adding person data with face data only 
    body = {
        "personCode": str(int(time.time())),
        "personFamilyName": "ring",
        "personGivenName": "face",
        "gender": 2,
        "orgIndexCode": "1",
        "faces": [
            {
                "faceData": face_base64
            }
        ],
        "beginTime": "2020-05-26T15:00:00+08:00",
        "endTime": "2030-05-26T15:00:00+08:00"
    }

    # Print the entire request body to debug
    print("Request Body:", json.dumps(body, indent=4))

    body_json = json.dumps(body)
    body_length = len(body_json)

    timestamp = str(int(time.time()))

    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/single/add"

    signature = hmac.new(
        app_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()

    signature_base64 = base64.b64encode(signature).decode('utf-8')

    headers = {
        'x-ca-key': app_key,
        'x-ca-signature': signature_base64,
        'Content-Type': 'application/json',
        'Timestamp': timestamp,
        'userId': 'admin',
    }

    try:
        print("Sending request to add person with face data...")
        response = requests.post(url_person_add, headers=headers, json=body)

        if response.status_code == 200:
            print("\nResponse received: Person added successfully.")
            print("Full response:", response.json())
            person_data = response.json()
            person_id = person_data.get("data")  # Corrected line to get the person ID from the 'data' field
            print(f"Person ID: {person_id}")
            return person_id
        else:
            print(f"Request failed with status code: {response.status_code}")
            print("Response content:", response.text)
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

    # Convert body to JSON string for API request
    body_json = json.dumps(body)
    body_length = len(body_json)

    # Get the current timestamp (seconds since epoch)
    timestamp = str(int(time.time()))

    # Prepare the string to sign for API authentication
    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/acs/v1/privilege/group/single/addPersons"

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
        'userId': 'admin',  # Replace 'admin' with actual userId if needed
    }

    # Send the POST request to add the person to the privilege group
    try:
        print("Sending request to add person to privilege group...")
        response = requests.post(url_privilege_group_add, headers=headers, json=body)

        # Print the response status and content for debugging
        print(f"Response Status Code: {response.status_code}")  # Log the status code
        print(f"Response Text: {response.text}")  # Log the raw response

        if response.status_code == 200:
            print(f"Person {person_id} added to the privilege group successfully.")
        else:
            print(f"Failed to add person to privilege group. Status code: {response.status_code}")
            print("Error Details:", response.json())  # Log error details for better debugging
    except requests.exceptions.RequestException as e:
        print(f"Error during the privilege group request: {e}")
    

# Example usage:
def main():
    print("Starting the program...")
    face_data = capture_face_data_with_retry() 
    if face_data:
        person_id = add_person_with_face(face_data) 
        if person_id:
            print(f"Person added successfully. Person ID: {person_id}")
            print("Adding person to privilege group...")
            add_person_to_privilege_group(person_id)
        else:
            print("Failed to add person.")
    else:
        print("Failed to process the face image.")

if __name__ == "__main__":
    main()
 