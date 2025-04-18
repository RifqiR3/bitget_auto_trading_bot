from bitget_auth import get_futures_account_info
from bitget_order import place_order
import json

def execute_trade(signal):
    # 1. Get account info
    account_data = get_futures_account_info()
    available_balance = float(account_data["data"]["available"])

    # 2. Extract values
    margin_pct = 0.15
    leverage = int(signal["leverage"].replace("X", ""))
    entry_price = float(signal["entry"])

    # 3. Calculate size
    position_value = available_balance * margin_pct * leverage
    size = round(position_value / entry_price, 3)

    direction = "buy" if signal["direction"] == "LONG" else "sell"

    # 4. Place order
    print(f"\nPlacing {direction.upper()} order for {signal['symbol']} at {entry_price} with size {size}")
    result = place_order(signal["symbol"], direction, signal["entry"], size, signal["sl"], signal["tp2"])
    print(json.dumps(result, indent=2))
    return result
