import requests
import json

BASE = "http://127.0.0.1:5000/"
get_response = requests.get(BASE + 'GetTrackInfo')  # Include the route path

# Check if the request was successful (status code 200)
if get_response.status_code == 200:
    # data = get_response.json()  # Parse the JSON response
    print(get_response.text)
else:
    print(f"Request failed with status code {get_response.status_code}")