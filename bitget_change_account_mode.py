from bitget_order import change_to_unilateral
import json

response = change_to_unilateral()
print(json.dumps(response, indent=2))
