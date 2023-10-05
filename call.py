import requests

id = '0X6onE002e0PuXSdVZmlDF'

base = 'http://127.0.0.1:5000/'
link = f"song/currentlyplaying/"
headers = {}

get_request = requests.get(base+link, headers=headers)

print(get_request.status_code)
print(get_request.json())