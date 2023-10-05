# routes.py
from flask import redirect, url_for, session, jsonify, request
import spotipy
import time
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from app import app, api
from resources import add_song, get_song
from models import SongModel

TOKEN_INFO = 'TOKEN_INFO'

# Define your routes and route handlers here
@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('GetTrackInfo', _external = True))

@app.route('/GetTrackInfo')
def GetTrackInfo():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_playback()
    if results:

        ## code here to query the previous song and mark currently_playing to false

        song_id = results['item']['id']
        song_name = results['item']['name']
        album_id = results['item']['album']['id']
        album_name = results['item']['album']['name']
        artist_name = results['item']['artists'][0]['name']
        length = results['item']['duration_ms']

        track_info = {
            'id' : str(song_id),
            'song_name': str(song_name),
            'album_name' : str(album_name),
            'aritst_name' : str(artist_name),
            'length' : str(length),
            'currently_playing': True
        }
        # Add song info to database
        link = (f'song/add/{str(track_info["id"])}')
        link = (f'song/add/')

        BASE = "http://127.0.0.1:5000/"
        headers = {'Content-Type': 'application/json'}
        track_info_json = json.dumps(track_info)
        put_response = requests.put(BASE + link, data=track_info_json, headers=headers)

        # this will probably change to returning a response code once I am further on in the project
        print(str(f"Song: {track_info['song_name']} Album: {track_info['album_name']} Artist: {track_info['aritst_name']} Length: {track_info['length']}"))
        return jsonify({'content': str(put_response.status_code)})
    else:
        return jsonify({'error': 'Nothing is currently playing'})

def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('redirect', external = False))

    now = int(time.time())
    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(client_id = client_id, 
                        client_secret = client_secret,
                        redirect_uri = url_for('redirect_page', _external=True),
                        scope = 'user-read-private user-read-currently-playing user-read-playback-state'
                        )
def handle_error(e):
    return jsonify(error=str(e)), 500