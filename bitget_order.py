import requests
import time
import hmac
import hashlib
import base64
import json
import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from decimal import Decimal, ROUND_DOWN, ROUND_UP

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

def change_to_unilateral():
    url = BASE_URL + "/api/v2/mix/account/set-position-mode"
    method = "POST"
    timestamp = get_timestamp()

    body_dict = {
	"productType": "USDT-FUTURES",
	"posMode": "one_way_mode"
    }

    body = json.dumps(body_dict)
    request_path = "/api/v2/mix/account/set-position-mode"
    message = pre_hash(timestamp, method, request_path, body)
    signature = sign(message, SECRET_KEY).decode()

    headers = {
        "ACCESS-KEY": API_KEY,
        "ACCESS-SIGN": signature,
        "ACCESS-TIMESTAMP": timestamp,
        "ACCESS-PASSPHRASE": PASSPHRASE,
        "Content-Type": "application/json"
    }

    print(url)

    response = requests.post(url, headers=headers, data=body)
    return response.json()

def format_price(price, precision, side):
    """
    Formats price based on precision and side (buy/sell).
    Buys round DOWN, sells round UP.
    """

    price = str(price)
    if '.' in price:
        whole, decimals = price.split('.')
        if len(decimals) > precision:
           quantize_str = '0.' + '0' * (precision - 1) + '1'  # e.g., '0.01' if precision=2
           decimal_price = Decimal(str(price))

           if side == "buy":
              rounded = decimal_price.quantize(Decimal(quantize_str), rounding=ROUND_DOWN)
           else:
              rounded = decimal_price.quantize(Decimal(quantize_str), rounding=ROUND_UP)

           return str(rounded)
        else:
           return str(price)
    else:
        return str(price)

def fetch_symbol_precisions():
    url = "https://api.bitget.com/api/v2/mix/market/contracts"
    params = {"productType": "usdt-futures"}

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("code") == "00000":
            precisions = {}
            for item in data["data"]:
                symbol = item["symbol"]
                price_place = item["pricePlace"]
                precisions[symbol] = price_place
            return precisions
        else:
            print(f"⚠️ Failed to fetch precisions: {data.get('msg')}")
            return {}
    except Exception as e:
        print(f"❌ Error fetching symbol precisions: {e}")
        return {}

symbol_precisions = fetch_symbol_precisions()


def place_order(symbol, side, entry_price, size, sl, tp2, margin_coin="USDT", product_type="USDT-FUTURES"):
    url = BASE_URL + "/api/v2/mix/order/place-order"
    method = "POST"
    timestamp = get_timestamp()

    # Get prices precision
    precision = symbol_precisions.get(symbol.upper() + "USDT")

    # Format prices
    entry_price = format_price(entry_price, precision, side)
    sl = format_price(sl, precision, "buy" if side == "sell" else "sell")
    tp2 = format_price(tp2, precision, side)
    print(entry_price)
    print(tp2)
    print(sl)

    body_dict = {
        "symbol": symbol.upper() + "USDT",
        "marginCoin": margin_coin,
	"marginMode": "crossed",
        "size": size,
        "price": entry_price,
	"posMode": "single_holding",
        "side": side,
        "orderType": "limit",
        "force": "gtc",
        "productType": product_type,
	"presetStopSurplusPrice": tp2,
	"presetStopLossPrice": sl
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


def save_order(order_data, filename="active_orders.json"):
	filepath = Path(filename)
	if filepath.exists():
		with open(filepath, "r") as f:
			orders = json.load(f)
	else:
		orders = []

	orders.append(order_data)

	with open(filepath, "w") as f:
		json.dump(orders, f, indent=2)
