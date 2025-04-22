import requests
from fastapi import FastAPI
from requests.auth import HTTPDigestAuth
from pydantic import BaseModel

# FastAPI instance
app = FastAPI()

# Device information
ip_address = "192.168.1.50"  # Your device's IP address
port = "80"                   # The port number
username = "admin"            # Replace with your username
password = "Admin123"         # Replace with your password

# Define the URL for capturing card information
capture_card_url = f"http://{ip_address}:{port}/ISAPI/AccessControl/CaptureCardInfo?format=json"

# Create a Pydantic model for the response
class CardInfoResponse(BaseModel):
    card_number: str

# Function to retrieve the card number
def get_card_number():
    auth = HTTPDigestAuth(username, password)
    response = requests.get(capture_card_url, auth=auth)
    
    if response.status_code == 200:
        card_info = response.json()
        card_number = card_info.get('CardInfo', {}).get('cardNo', None)
        
        if card_number:
            return card_number
        else:
            return None
    else:
        return None

# Define a FastAPI endpoint to get the card number
@app.get("/get-card-number", response_model=CardInfoResponse)
async def get_card_number_endpoint():
    card_number = get_card_number()
    
    if card_number:
        return CardInfoResponse(card_number=card_number)
    else:
        return {"message": "Card number not found"}
