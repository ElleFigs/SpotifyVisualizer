import requests
import json

BASE = "http://127.0.0.1:5000/"
data = [{
        "name": "Rhiannon", 
        "artist":"Fleetwood Mac", 
        "album":"Fleetwood Mac",
        "length": 252
    },
    {
        "name": "Is this it", 
        "artist":"The Strokes", 
        "album":"Is this it",
        "length": 180
    },
    {
        "name": "Black Dog", 
        "artist":"Led Zeppelin", 
        "album":"Led Zeppelin IV",
        "length": 295
    },
    {
        "name": "Tumbling Dice", 
        "artist":"The Rolling Stones", 
        "album":"Exile On Main Street",
        "length": 226
    }]

headers = {'Content-Type': 'application/json'}
i=0

while i < len(data):
    data_json = json.dumps(data[i])
    link = (f'song/{i}')
    put_response = requests.put(BASE + link, data=data_json, headers=headers)
    i+=1

j = 0
while j < len(data):
    link = (f'song/{j}')
    get_response = requests.get(BASE + link)
    print(get_response.json())
    j+=1

song_id_to_delete = 'song/2'
del_response = requests.delete(BASE + song_id_to_delete)
print(del_response)

j = 0
while j < len(data):
    link = (f'song/{j}')
    get_response = requests.get(BASE + link)
    print(get_response.json())
    j+=1
