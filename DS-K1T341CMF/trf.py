import base64
import hashlib
import hmac
import json
import time
import requests

# API credentials and URLs
app_key = '27435223' 
app_secret = 'J194LCQU62Sl81YSYBkg'  
url_person_add = "http://196.224.39.92/artemis/api/resource/v1/person/single/add"  # API endpoint for adding person
url_privilege_group_add = "http://196.224.39.92/artemis/api/acs/v1/privilege/group/single/addPersons"  # API endpoint for adding to privilege group

# Device information 
ip_address = "192.168.1.32"    
port = "80"                   
username = "admin"           
password = "Admin123"         

# Function to read an image file and convert it to Base64
def image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            # Read the image and encode it in base64
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

            # Check if the Base64 string starts with "/9j" and ends with "/Z"
            if encoded_image.startswith("/9j") and encoded_image.endswith("/Z"):
                print("Image Base64 encoded correctly!")
            else:
                print("Warning: Base64 image does not start with '/9j' or end with '/Z'.")

            print(f"Base64 Encoded Image: {encoded_image[:50]}...")  # Print first 50 characters for reference
            return encoded_image
    except Exception as e:
        print(f"Error reading or encoding image: {e}")
        return None

# Function to add person data with face data (Base64 encoded) to the system
def add_person_with_face(face_data):
    if not face_data:
        print("No face data to add.")
        return

    # Manually setting beginTime and endTime to ensure proper format
    begin_time = "2025-02-10T00:00:00+08:00"  # Example of beginTime (ISO 8601 format with timezone)
    end_time = "2030-02-10T23:59:59+08:00"    # Example of endTime (ISO 8601 format with timezone)

    # Prepare body for adding person data with face data only 
    body = {
        "personCode": str(int(time.time())),  # Generate unique person code using current timestamp
        "personFamilyName": "ring",
        "personGivenName": "face",
        "gender": 2,
        "orgIndexCode": "1",
        "faces": [
            {
                "faceData": face_data  # Face data is passed as Base64 encoded string
            }
        ],
        "beginTime": begin_time,  # Use the manually set beginTime
        "endTime": end_time       # Use the manually set endTime
    }

    # Convert body to JSON string for API request
    body_json = json.dumps(body)
    body_length = len(body_json)

    # Get the current timestamp (seconds since epoch)
    timestamp = str(int(time.time()))

    # Prepare the string to sign for API authentication
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

        # Print the response status and content for debugging
        print(f"Response Status Code: {response.status_code}")  # Log the status code
        print(f"Response Text: {response.text}")  # Log the raw response

        if response.status_code == 200:
            print("\nResponse received: Person added successfully.")
            response_data = response.json()
            print(json.dumps(response_data, indent=4))  # Debugging: Print the entire response

            # Check if the response contains the person ID
            person_id = response_data.get("data")
            print(f"Person ID: {person_id}")

            # Return the person ID
            return person_id
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

# Main function to drive the program
def main():
    print("Starting the program...")

    # Example of how to use the image-to-Base64 function
    image_path = r"C:\Users\Chaima\Desktop\server\WhatsApp.jpeg"
    face_data = image_to_base64(image_path) 

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
