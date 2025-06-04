import time
import json
import base64
import hashlib
import hmac
import requests
from requests.auth import HTTPDigestAuth

# Your API keys and endpoint details
app_key = '27435223'
app_secret = 'J194LCQU62Sl81YSYBkg'
url = "http://196.224.39.92/artemis/api/resource/v1/person/single/add"
url_privilege_group_add = "http://196.224.39.92/artemis/api/acs/v1/privilege/group/single/addPersons"

# Device information
ip_address = "192.168.1.32"  # Your device's IP address
port = "80"                   # The port number
username = "admin"            # Replace with your username
password = "Admin123"         # Replace with your password

# Function to add a person
def add_person():
    # Create the body for adding a person (without card information)
    body = {
        "personCode": str(int(time.time())),
        "personId": "2",     # Update with actual person ID
        "personFamilyName": "testing",  # Replace with the family name
        "personGivenName": "new",  # Replace with the given name
        "orgIndexCode": "1",  # Update with the appropriate organization code
        "phoneNo": "1234",    # Replace with the phone number
        # "cards": [{"cardNo": card_no}],  # Removed card information
        "beginTime": "2020-05-26T15:00:00+08:00",  # Set the begin time
        "endTime": "2030-05-26T15:00:00+08:00"    # Set the end time
    }

    # Convert body to JSON string
    body_json = json.dumps(body)
    body_length = len(body_json)

    # Current timestamp (seconds since epoch)
    timestamp = str(int(time.time()))

    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/single/add"

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

# Function to add person to privilege group
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

# Main function to control the flow
def main():
    print("Starting the program...")
    
    # Add a person and get their ID
    person_id = add_person()

    if person_id:
        print(f"Person added successfully. Person ID: {person_id}")
        print("Adding person to privilege group...")
        add_person_to_privilege_group(person_id)
    else:
        print("Failed to add person.")

if __name__ == "__main__":
    main()
