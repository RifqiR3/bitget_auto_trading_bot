from bitget_auth import get_futures_account_info
from bitget_order import place_order
import json

# 1. Get account info
account_data = get_futures_account_info()
available_balance = float(account_data["data"]["available"])

# 2. Sample signal
signal = {
    "direction": "LONG",
    "symbol": "SFP",
    "entry": "0.4459",
    "leverage": "20X",
    "sl": "0.4334",
    "tp1": "0.4484",
    "tp2": "0.4509"
}

# 3. Calculate position size based on available balance
margin_pct = 0.15
leverage = int(signal["leverage"].replace("X", ""))
entry_price = float(signal["entry"])

position_value = available_balance * margin_pct * leverage
size = round(position_value / entry_price, 3)

if signal["direction"] == "LONG":
	direction = "buy"
else:
	direction = "sell"

# 4. Place order
print(direction)
result = place_order(signal["symbol"], direction, signal["entry"], size, signal["sl"], signal["tp2"])
print(json.dumps(result, indent=2))
