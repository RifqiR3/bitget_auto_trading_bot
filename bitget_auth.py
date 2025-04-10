import requests
import time
import hashlib
import hmac
import json
import os
from dotenv import load_dotenv

load_dotenv()

# API Credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

# Step 1: Generate Signature
def generate_signature(timestamp, method, request_path, body=""):
    message = f"{timestamp}{method}{request_path}{body}"
    signature = hmac.new(
        SECRET_KEY.encode(), 
        message.encode(), 
        hashlib.sha256
    ).hexdigest()
    return signature

# Step 2: Fetch Account Info
def get_futures_account_info():
    # API Endpoint
    url = "https://api.bitget.com/api/mix/v1/account/accounts"
    method = "GET"
    request_path = "/api/mix/v1/account/accounts"
    
    # Timestamp (in milliseconds)
    timestamp = str(int(time.time() * 1000))
    
    # Generate signature (empty body for GET requests)
    signature = generate_signature(timestamp, method, request_path)
    
    # Headers
    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }
    
    # Send request
    response = requests.get(url, headers=headers)
    return response.json()

# Step 3: Execute
if __name__ == "__main__":
    try:
        account_info = get_futures_account_info()
        print("Futures Account Info:")
        print(json.dumps(account_info, indent=2))
    except Exception as e:
        print(f"Error: {e}")