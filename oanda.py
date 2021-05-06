import requests
import json
import numpy as np


API = "https://api-fxpractice.oanda.com"
STREAM_API =  	"https://stream-fxpractice.oanda.com/"

ACCESS_TOKEN = "2cad9d0b4f90ab15761da499b43c26ad-06f113d3baaf47ba500924d8bc93e0fa"
ACCOUNT_ID = "101-001-18827664-001" 

PRICING_PATH= "/v3/accounts/{"+ACCOUNT_ID+"}/pricing"
query = {"instruments" : "USD_CAD"}
headers = {"Authorization": "Bearer "+ ACCESS_TOKEN}

response = requests.get(API+PRICING_PATH, headers = headers, params = query)
print(response.json()) 