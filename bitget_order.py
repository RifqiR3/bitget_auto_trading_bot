import requests
import time
import hmac
import hashlib
import base64
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BITGET_API_KEY")
SECRET_KEY = os.getenv("BITGET_API_SECRET")
PASSPHRASE = os.getenv("BITGET_API_PASSPHRASE")

BASE_URL = "https://api.bitget.com"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(message, secret_key):
    mac = hmac.new(secret_key.encode(), message.encode(), digestmod='sha256')
    return base64.b64encode(mac.digest())

def pre_hash(timestamp, method, request_path, body):
    return f"{timestamp}{method.upper()}{request_path}{body}"

def place_order(symbol, side, entry_price, size, margin_coin="USDT", product_type="USDT-FUTURES"):
    url = BASE_URL + "/api/v2/mix/order/place-order"
    method = "POST"
    timestamp = get_timestamp()

    body_dict = {
        "symbol": symbol.upper() + "USDT",
        "marginCoin": margin_coin,
	"marginMode": "crossed",
        "size": size,
        "price": entry_price,
	"posMode": "hedge_mode",
        "side": side,
        "orderType": "limit",
        "force": "gtc",
        "productType": product_type
    }

    body = json.dumps(body_dict)
    request_path = "/api/v2/mix/order/place-order"
    message = pre_hash(timestamp, method, request_path, body)
    signature = sign(message, SECRET_KEY).decode()

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=body)
    return response.json()
