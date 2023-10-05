# routes.py
from flask import redirect, url_for, session, jsonify, request
import spotipy
import time
import requests
import json
import spotipy
import private
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy.exc import IntegrityError


from app import app, api, db, Session
from resources import add_song, get_song
from models import SongModel

TOKEN_INFO = 'TOKEN_INFO'

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

        song_id = results['item']['id']
        song_name = results['item']['name']
        album_id = results['item']['album']['id']
        album_name = results['item']['album']['name']
        artist_name = results['item']['artists'][0]['name']
        length = results['item']['duration_ms']

        track_info = {
            'song_id' : str(song_id),
            'song_name': str(song_name),
            'album_name' : str(album_name),
            'artist_name' : str(artist_name),
            'length' : str(length),
            'currently_playing': True
        }
        # Add song info to database
        session = Session()

        try:
            currently_playing_songs = session.query(SongModel).filter(SongModel.currently_playing == True).all()
            if currently_playing_songs:
                for song in currently_playing_songs:
                    song.currently_playing = False

            
            # Add song info to database within the session
            new_song = SongModel(
                song_id=track_info['song_id'],
                song_name=track_info['song_name'],
                artist_name=track_info['artist_name'],
                album_name=track_info['album_name'],
                length=track_info['length'],
                currently_playing = True
            )

            # Commit the changes to the database
            session.add(new_song)
            session.commit()

            print(str(f"Song: {track_info['song_name']} Album: {track_info['album_name']} Artist: {track_info['artist_name']} Length: {track_info['length']}"))

            # Close the session
            session.close()

            return str(f"Song: {track_info['song_name']} Album: {track_info['album_name']} Artist: {track_info['artist_name']} Length: {track_info['length']}")
        
        except IntegrityError as e:
            # Handle the IntegrityError (UNIQUE constraint violation)
            print(f"IntegrityError: {e}")
            session.rollback()
            return jsonify({'error': 'A song with the same song_id already exists in the database'})

        except Exception as e:
            # Handle other exceptions that may occur during database operations
            print(f"Error: {e}")
            session.rollback()
            return jsonify({'error': 'An error occurred while adding the song to the database'})

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
    return SpotifyOAuth(client_id = private.CLIENT_ID, 
                        client_secret = private.CLIENT_SECRET,
                        redirect_uri = url_for('redirect_page', _external=True),
                        scope = 'user-read-private user-read-currently-playing user-read-playback-state'
                        )
def handle_error(e):
    return jsonify(error=str(e)), 500