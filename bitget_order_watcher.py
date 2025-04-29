import asyncio
import json
import websockets
import os
import time
import requests
import uuid
from websockets.exceptions import ConnectionClosed
from bitget_order import get_timestamp, sign, pre_hash, API_KEY, PASSPHRASE, SECRET_KEY

ORDERS_FILE = "active_orders.json"

def is_order_filled(order_id, symbol):
	url = f"https://api.bitget.com/api/v2/mix/order/detail"
	method = "GET"
	timestamp = get_timestamp()
	query = f"symbol={symbol}&orderId={order_id}&productType=usdt-futures"
	request_path = f"/api/v2/mix/order/detail?{query}"

	message = pre_hash(timestamp, method, request_path, "")
	signature = sign(message, SECRET_KEY)

	headers = {
	  "ACCESS-KEY": API_KEY,
	  "ACCESS-SIGN": signature,
	  "ACCESS-TIMESTAMP": timestamp,
	  "ACCESS-PASSPHRASE": PASSPHRASE,
	  "Content-Type": "application/json"
	}

	try:
		response = requests.get(f"{url}?{query}", headers=headers)
		data = response.json()
		if data.get("code") == "00000" and data.get("data"):
			status = data["data"].get("state")
			print(f"🔎 Order state ({symbol}): {status}")
			return status == "filled"
		else:
			print(f"⚠️  Error: {data.get('msg')}")
			return False
	except Exception as e:
		print(f"❌ Error checking order status: {e}")
		return False

def modify_stop_loss(symbol, order_id, new_sl_price):
	url = "https://api.bitget.com/api/v2/mix/order/place-tpsl-order"
	method = "POST"
	timestamp = get_timestamp()

	order = next((o for o in load_orders() if o["orderId"] == order_id), None)
	if not order:
		print(f"⚠️ Could not find order with ID {order_id} in active_orders.json")
		return

	side = order["side"]
	# hold_side = "long" if side == "buy" else "short"

	body_dict = {
	  "symbol": symbol,
	  "marginCoin": "USDT",
	  "productType": "usdt-futures",
	  "planType": "pos_loss",
	  "triggerPrice": str(new_sl_price),
	  "triggerType": "fill_price",
	  "holdSide": side,
	  "size": "",
	  "clientOid": str(uuid.uuid4())
	}

	body = json.dumps(body_dict)
	request_path = "/api/v2/mix/order/place-tpsl-order"
	message = pre_hash(timestamp, method, request_path, body)
	signature = sign(message, SECRET_KEY)

	headers = {
	  "ACCESS-KEY": API_KEY,
	  "ACCESS-SIGN": signature,
	  "ACCESS-TIMESTAMP": timestamp,
	  "ACCESS-PASSPHRASE": PASSPHRASE,
	  "Content-Type": "application/json"
	}

	try:
		response = requests.post(url, headers=headers, data=body)
		data = response.json()
		if data.get("code") == "00000":
			print(f"✅ SL moved to breakeven ({new_sl_price}) for {symbol} ({order_id})")
		else:
			print(f"⚠️ Failed to modify SL via trigger order: {data.get('msg')}")
	except Exception as e:
		print(f"❌ Error modifying SL trigger order: {e}")

# Load active orders from the file
def load_orders():
	if os.path.exists(ORDERS_FILE):
		with open(ORDERS_FILE, "r") as f:
			return json.load(f)

	return []

# Save orders back to the file
def save_orders(orders):
	with open(ORDERS_FILE, "w") as f:
		json.dump(orders, f, indent=2)


# Subscribe to tickers for all tracked symbols in the file
def build_sub_payload(symbols):
	args = [{"instType": "USDT-FUTURES", "channel": "ticker", "instId": s} for s in symbols]
	return {
	"op": "subscribe",
	"args": args
	}

async def connect_and_watch():
	while True:
		try:
			await watch_orders()
		except ConnectionClosed as e:
			print(f"🔌 WebSocket disconnected: {e}. Reconnecting in 5s...")
			await asyncio.sleep(5)
		except Exception as e:
			print(f"❌ Unexpected error: {e}. Restarting in 5s...")
			await asyncio.sleep(5)

async def watch_orders():
	url = "wss://ws.bitget.com/v2/ws/public"

	orders = load_orders()
	if not orders:
		print("No active orders to watch")
		return

	symbols = list(set([o["symbol"] for o in orders]))

	async with websockets.connect(url) as ws:
		await ws.send(json.dumps(build_sub_payload(symbols)))
		print(f"📡 Subscribed to: {symbols}")

		while True:
			orders_changed = False
			msg = await ws.recv()
			data = json.loads(msg)

			if "data" in data and "arg" in data:
				tick = data["data"][0]
				symbol = data["arg"]["instId"]
				price = float(tick["lastPr"])

				print(f"[{symbol}] 💹 Price: {price}")

				updated_orders = []
				for order in orders:
					if order["symbol"] != symbol:
						updated_orders.append(order)
						continue

					entry = float(order["entry"])
					tp1 = float(order["tp1"])
					tp2 = float(order["tp2"])
					sl = float(order["sl"])
					order_id = order["orderId"]
					side = order["side"]

					if not order.get("filled"):
						if is_order_filled(order["orderId"], order["symbol"]):
							order["filled"] = True
							orders_changed = True
							print(f"✅ Order {order['orderId']} is filled. Tracking started. ")
						updated_orders.append(order)
						continue

					tp_hit = price >= tp1 if side == "buy" else price <= tp1
					tp2_hit = price >= tp2 if side == "buy" else price <= tp2
					sl_hit = price <= sl if side == "buy" else price >= sl

					if tp_hit and not order["tp1_hit"]:
						print(f"🎯 TP1 hit for {symbol} ({order_id})! Moving SL to breakeven.")
						order["sl"] = entry
						order["tp1_hit"] = True
						orders_changed = True
						updated_orders.append(order)
						modify_stop_loss(symbol, order_id, entry)
					elif tp2_hit and order["tp1_hit"]:
						print(f"🎯 TP2 hit for {symbol} ({order_id})! Removing order.")
						orders_changed = True
						continue
					elif sl_hit:
						print(f"🛑 SL hit for {symbol} ({order_id})! Removing order.")
						orders_changed = True
						continue
					else:
						updated_orders.append(order)

				if orders_changed:
					save_orders(updated_orders)
					orders = updated_orders

asyncio.run(connect_and_watch())
