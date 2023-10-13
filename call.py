import requests
import pandas as pd
import json

base = 'http://127.0.0.1:5000/'
link = f"/song/currentlyplaying/"
headers = {}

get_request = requests.get(base+link)
response_json_list = get_request.json()
print(response_json_list)

# response_json = json.dumps(get_request.json())
# df = pd.read_json(response_json)
# print(df.columns)
