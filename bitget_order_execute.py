from bitget_auth import get_futures_account_info
from bitget_order import place_order, save_order, format_price, symbol_precisions
import json

def execute_trade(signal):
    precision = symbol_precisions.get(signal["symbol"].upper() + "USDT")
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
    result = place_order(signal["symbol"], direction, signal["entry"], str(size), signal["sl"], signal["tp2"])
    print(json.dumps(result, indent=2))

    # 5. Save order to track
    order_data = {
    	"symbol": signal["symbol"].upper() + "USDT",
        "side": direction,
	"entry": format_price(signal["entry"], precision, direction),
	"tp1": format_price(signal["tp1"], precision, direction),
	"tp2": format_price(signal["tp2"], precision, direction),
	"sl": format_price(signal["sl"], precision, "buy" if direction == "sell" else "sell"),
	"orderId": result["data"]["orderId"],
	"tp1_hit": False,
	"filled": False
    }
    save_order(order_data)
    print(f"Position {order_data['orderId']} is saved")
    return result
