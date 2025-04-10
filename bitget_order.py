from bitget_auth import generate_headers, BASE_URL
import requests
import json

path = "/api/mix/v1/account/accounts?productType=USDT"
url = BASE_URL + path

headers = generate_headers("GET", path)
resp = requests.get(url, headers=headers)

print(resp.status_code)
print(resp.json())