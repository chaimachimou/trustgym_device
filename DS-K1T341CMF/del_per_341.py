import time
import json
import base64
import hashlib
import hmac
import requests
from requests.auth import HTTPDigestAuth

# Your API keys and endpoint details for the signature-based request
app_key = '27435223'
app_secret = 'J194LCQU62Sl81YSYBkg'
url = "http://127.0.0.1:9016/artemis/api/resource/v1/person/single/delete"

# Device information for the second API request
ip_address = "192.168.1.32"  # Your device's IP address
port = "80"                   # The port number
username = "admin"            # Update with your username
password = "Admin123"         # Update with your password

# Generate the API signature
def generate_signature(body_json):
    timestamp = str(int(time.time()))
    string_to_sign = f"POST\n*/*\napplication/json\n/artemis/api/resource/v1/person/single/delete"
    
    # Generate HMAC SHA256 signature
    signature = hmac.new(
        app_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    signature_base64 = base64.b64encode(signature).decode('utf-8')
    
    return signature_base64, timestamp

# Function to delete a user by employee number
def delete_user_by_employee_no(employee_no):
    delete_url = f"http://{ip_address}:{port}/ISAPI/AccessControl/UserInfoDetail/Delete?format=json"
    
    payload = {
        "UserInfoDetail": {
            "mode": "byEmployeeNo",
            "EmployeeNoList": [
                {
                    "employeeNo": employee_no
                }
            ]
        }
    }

    try:
        print("Sending deletion payload:")
        print(json.dumps(payload, indent=4))
        
        response = requests.put(
            delete_url,
            auth=HTTPDigestAuth(username, password),
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload)
        )
        
        print(f"Request URL: {delete_url}")
        print(f"Response Code: {response.status_code}")
        
        if response.status_code == 200:
            print("Deletion started successfully.")
            # Call function to check deletion status
            check_deletion_status(employee_no)
        else:
            handle_error(response)
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Function to check the status of the deletion process
def check_deletion_status(employee_no):
    status_url = f"http://{ip_address}:{port}/ISAPI/AccessControl/UserInfoDetail/DeleteProcess?format=json"
    
    while True:
        response = requests.get(status_url, auth=HTTPDigestAuth(username, password))
        if response.status_code == 200:
            status_data = response.json()
            status = status_data.get("UserInfoDetailDeleteProcess", {}).get("status")
            print(f"Current deletion status: {status}")
            
            if status in ["success", "failed"]:
                print("Deletion process completed.")
                break
        else:
            handle_error(response)
        
        time.sleep(5)  # Wait for a bit before checking again

# Function to handle errors
def handle_error(response):
    response_content = response.json()
    print("Failed to start deletion.")
    print(f"Status Code: {response_content.get('statusCode')}")
    print(f"Status String: {response_content.get('statusString')}")
    print(f"Sub Status Code: {response_content.get('subStatusCode')}")
    print(f"Error Code: {response_content.get('errorCode')}")
    print(f"Error Message: {response_content.get('errorMsg')}")

# Function to delete a person via the signature-based API
def delete_person_via_signature(person_id):
    body = {
        "personId": person_id,
    }

    body_json = json.dumps(body)
    signature_base64, timestamp = generate_signature(body_json)
    
    headers = {
        'x-ca-key': app_key,
        'x-ca-signature': signature_base64,
        'Content-Type': 'application/json',
        'Timestamp': timestamp,
        'userId': 'admin',
    }

    try:
        print("Sending signature-based deletion request:")
        response = requests.post(url, headers=headers, json=body)
        
        if response.status_code == 200:
            print("\nResponse received:")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"Error during the request: {e}")

# Main execution
if __name__ == "__main__":
    # Delete by employee number
    employee_no = input("Enter the employee number to delete: ")
    print(f"Attempting to delete employee number: {employee_no}")
    delete_user_by_employee_no(employee_no)
    
    # Optionally delete via personId (for the first API)
    person_id = input("Enter the personId to delete via signature-based API: ")
    delete_person_via_signature(person_id)
