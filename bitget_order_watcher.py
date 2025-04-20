import asyncio
import json
import websockets
import os

ORDERS_FILE = "active_orders.json"

# Load active orders from the file
def load_order():
	if os.path.exists(ORDER_FILE)
		with open(ORDER_FILE, "r") as f:
			return json.load(f)

	return []

# Save orders back to the file
def save_orders(orders):
	with open(ORDERS_FILE, "w") as f:
		json.dump(orders, f, indent=2)


# Subscribe to tickers for all tracked symbols in the file
def build_sub_payload(symbols):
	args = [{"instId": s, "channel": "ticker"} for s in symbols]
	return {
	"op": "subscribe",
	"args": args
	}

async def watch_orders():
	url = "wss://ws.bitget.com/mix/v1/stream"

	orders = load_orders()
	if not orders:
		print("No active orders to watch")
		return

	symbols = list(set([o["symbol"] for o in orders]))

	async with websockets.connect(url) as ws:
		await ws.send(json.dumps(build_sub_payload(symbols)))
		print(f"📡 Subscribed to: {symbols}")

		while True:
			msg = await ws.recv()
			data = json.loads(msg)

			if "data" in data:
				tick = data["data"]
				symbol = data["args"]["instId"]
				price = float(tick["last"])

			updated_orders = []
			for order in orders:
				if order["symbol"] != symbol:
					updated_orders.append()
					continue

				entry = float(order("entry"))
				tp1 = float(order["tp1"])
				sl = float(order["sl"])
				order_id = order["orderId"]
				side = order["side"]

				tp_hit = price >= tp1 if side == "buy" else price <= tp1
				sl_hit = price <= sl if side == "buy" else price >= sl

				if tp_hit:
					print(f"🎯 TP1 hit for {symbol} ({order_id})! Moving SL to breakeven.")
					order["sl"] = entry
					updated_orders.append(order)
				elif sl_hit:
					print(f"🛑 SL hit for {symbol} ({order_id})! Removing order.")
				else:
					updated.orders.append(order)

			if updated_orders != orders:
				save_orders(updated_orders)
				orders = updated_orders

asyncio.run(watch_orders())
