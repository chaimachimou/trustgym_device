from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import base64
import hmac
import hashlib
import time
from datetime import datetime, timezone

app = FastAPI()

# Define API credentials
app_key = "26737313"
app_secret = "VMCICEDXszmI4z8bYSlm"
base_url = "http://127.0.0.1:9016/artemis/api/resource/v1/person/advance/personList"

# Request payload model for validation
class PersonRequest(BaseModel):
    pageNo: int
    pageSize: int
    personName: str
    cardNo: str

@app.post("/check_person_end_time")
async def check_person_end_time(request: PersonRequest):
    # Generate a timestamp
    timestamp = str(int(time.time() * 1000))  # Current timestamp in milliseconds

    # Prepare the body of the request using data from incoming request
    payload = request.dict()

    # String to sign for API authentication
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

    try:
        response = requests.post(base_url, headers=headers, json=payload, verify=False)
        response.raise_for_status()  # Check for HTTP errors

        # Assuming the response is in JSON format, process it accordingly
        response_data = response.json()

        # Check if the 'data' field contains a 'list' of users
        people = response_data.get('data', {}).get('list', [])

        if not people:
            # If no members are found, raise a 404 HTTPException with a custom message
            raise HTTPException(status_code=404, detail="member not found")

        # If members are found, check their 'endTime' against the current time
        results = []
        for person in people:
            end_time = person.get('endTime')
            if end_time:
                # Convert endTime to a datetime object (adjusted format)
                end_time_datetime = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S%z")

                # Get the current time as a timezone-aware datetime object (UTC)
                current_time = datetime.now(timezone.utc)

                # Compare endTime with current time and append the result
                results.append(end_time_datetime > current_time)
            else:
                results.append(False)  # If no endTime is found, return False

        return {"results": results}

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error with the external API request")
