import requests
import pandas as pd
import json

link = "http://127.0.0.1:5000/song/currentlyplaying/"
track_info = requests.get(link)
response_json = track_info.json()
# track_info_json = json.dumps(track_info.json())
# df = pd.read_json(track_info_json)
# print(df.head())

# print(f"Song ID: {response_json['song_id']}")
print(f"Song Name: {response_json['song_name']}")
# print(f"Artist Name: {response_json['artist_name']}")
# print(f"Album Name: {response_json['album_name']}")