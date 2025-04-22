import time
import json
import base64
import hashlib
import hmac
import uuid
import traceback
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
from httpx import DigestAuth, ReadTimeout

# API keys and endpoint details
app_key = '26737313'
app_secret = 'VMCICEDXszmI4z8bYSlm'
url_add_person = "http://127.0.0.1:9016/artemis/api/resource/v1/person/single/add"
url_privilege_group_add = "http://127.0.0.1:9016/artemis/api/acs/v1/privilege/group/single/addPersons"

# Device information
ip_address = "192.168.1.50"
port = "80"
username = "admin"
password = "Admin123"
capture_card_url = f"http://{ip_address}:{port}/ISAPI/AccessControl/CaptureCardInfo?format=json"

# FastAPI app instance
app = FastAPI()

# Request schema
class PersonRequest(BaseModel):
    person_family_name: str
    person_given_name: str
    org_index_code: str
    phone_no: str

# Function to create HMAC signature
def create_signature(path: str) -> str:
    string_to_sign = f"POST\n*/*\napplication/json\n{path}"
    signature = hmac.new(
        app_secret.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha256
    ).digest()
    return base64.b64encode(signature).decode('utf-8')

# Function to add person to privilege group
async def add_person_to_privilege_group(client: httpx.AsyncClient, person_id: str):
    body = {
        "privilegeGroupId": "1",  # Static group ID as requested
        "type": 1,
        "list": [{"id": person_id}]
    }

    headers = {
        'x-ca-key': app_key,
        'x-ca-signature': create_signature("/artemis/api/acs/v1/privilege/group/single/addPersons"),
        'Content-Type': 'application/json',
        'Timestamp': str(int(time.time())),
        'userId': 'admin',
    }

    try:
        response = await client.post(url_privilege_group_add, headers=headers, json=body)
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        if response.status_code == 200:
            print(f" Person {person_id} added to privilege group automatically.")
        else:
            print(f" Failed to add person to privilege group. Status: {response.status_code}")
    except httpx.RequestError as e:
        print(f" Error during privilege group request: {e}")

# Function to add person and capture card info
async def add_person(client: httpx.AsyncClient, person_data: PersonRequest):
    try:
        response = await client.get(capture_card_url, auth=DigestAuth(username, password))
        response.raise_for_status()
        data = response.json()

        if "CardInfo" not in data or "cardNo" not in data["CardInfo"]:
            return {"message": " No valid card number found."}

        card_no = data["CardInfo"]["cardNo"]
        person_id = str(uuid.uuid4())
        body = {
            "personCode": str(int(time.time())),
            "personId": person_id,
            "personFamilyName": person_data.person_family_name,
            "personGivenName": person_data.person_given_name,
            "orgIndexCode": person_data.org_index_code,
            "phoneNo": person_data.phone_no,
            "cards": [{"cardNo": card_no}],
            "beginTime": "2020-05-26T15:00:00+08:00",
            "endTime": "2030-05-26T15:00:00+08:00"
        }

        headers = {
            'x-ca-key': app_key,
            'x-ca-signature': create_signature("/artemis/api/resource/v1/person/single/add"),
            'Content-Type': 'application/json',
            'Timestamp': str(int(time.time())),
            'userId': 'admin',
        }

        add_response = await client.post(url_add_person, headers=headers, json=body)
        response_data = add_response.json()

        if add_response.status_code == 200 and "data" in response_data:
            real_person_id = response_data["data"]
            await add_person_to_privilege_group(client, real_person_id)
            return {
                "person_id": real_person_id,
                "card_no": card_no,
                "message": " Person added with captured card and assigned to privilege group.",
                "full_response": response_data
            }
        else:
            return {
                "message": " Failed to add person.",
                "full_response": response_data
            }

    except ReadTimeout:
        return {"message": " Request timed out."}
    except httpx.HTTPStatusError as e:
        print(f" HTTP error: {e}")
        return {"message": "HTTP error occurred."}
    except Exception as e:
        traceback.print_exc()
        return {"message": f"Unexpected error: {str(e)}"}

# FastAPI route
@app.post("/add_person/")
async def create_person(person_request: PersonRequest):
    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:
        result = await add_person(client, person_request)
        if result:
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to add person.")
