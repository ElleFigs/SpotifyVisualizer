import requests
import json

track_info = {
        "id": "1239",
        "song_name": "The Chain", 
        "artist_name":"Fleetwood Mac", 
        "album_name":"Fleetwood Mac",
        "length": 252
    }

BASE = "http://127.0.0.1:5000/"
link = f"song/add/{track_info['id']}"

headers = {'Content-Type': 'application/json'}
track_info_json = json.dumps(track_info)

put_response = requests.put(BASE + link, data=track_info_json, headers=headers)
print(put_response.status_code)


