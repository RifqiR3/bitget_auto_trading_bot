import requests
import time
import hmac
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load API credentials
API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(message, secret_key):
    mac = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), digestmod='sha256')
    return base64.b64encode(mac.digest()).decode()

def parse_params_to_str(params):
    sorted_params = sorted(params.items())
    return '?' + '&'.join([f"{key}={value}" for key, value in sorted_params])

def generate_headers(method, request_path, body=""):
    timestamp = get_timestamp()
    message = f"{timestamp}{method.upper()}{request_path}{body}"
    signature = sign(message, SECRET_KEY)

    return {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

def get_futures_account_info():
    method = "GET"
    base_path = "/api/v2/mix/account/account"
    params = {
	"symbol": "btcusdt",
	"marginCoin": "usdt",
	"productType": "USDT-FUTURES"
    }
    query_str = parse_params_to_str(params)
    request_path = base_path + query_str
    url = BASE_URL + request_path
    # print("Request URL:", url)
    
    headers = generate_headers(method, request_path)
    # print("Headers:", headers)
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == "__main__":
    result = get_futures_account_info()
    print("Futures Account Info:")
    print(json.dumps(result, indent=2))
