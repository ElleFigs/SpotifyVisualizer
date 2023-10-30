# routes.py
from flask import redirect, url_for, session, jsonify, request, render_template
import spotipy
import time
import requests
import json
import spotipy
import private
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy.exc import IntegrityError
import dash
from dash import html


from app import app, api, db, Session
from resources import add_song, get_song
from models import SongModel, AudioAnalysis

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
    return redirect(url_for('homepage_page', _external = True))

@app.route('/HomePage')
def homepage_page():
    return render_template('home_page.html')

@app.route('/createrecent25playlist')
def create_recent_25_playlist():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_user = sp.current_user()
    
    def check_if_recent_25_exists():
    
        playlist_info = {}
        offset = 0
        limit = 50
        recent_25_playlist_exists = False

        while True:
            playlists = sp.current_user_playlists(offset=offset, limit=limit)
            if not playlists['items']:
                break

            for item in playlists['items']:
                playlist_info[item['name']] = item['id']

            offset += limit

        if 'Recent 25 Tracks' in playlist_info:
            recent_25_playlist_exists = True
            recent_25_playlist_id = playlist_info['Recent 25 Tracks']
            return recent_25_playlist_exists, recent_25_playlist_id
        else:
            return recent_25_playlist_exists, False
    
    def get_recent_25_tracks():
        tracks = sp.current_user_recently_played(limit = 25)['items']
        track_uris = []
        for track_no in range(len(tracks)):
            track_uris.append(tracks[track_no]['track']['uri'])

        return track_uris
    
    
    def create_recent_25_tracks_playlist():
        
        recent_25_playlist_exists = check_if_recent_25_exists()
        
        if recent_25_playlist_exists[0] == False:

            playlist = sp.user_playlist_create(
                user = current_user['id'],
                name = 'Recent 25 Tracks',
                public = False
            )

            track_uris = get_recent_25_tracks()
            
            sp.playlist_add_items(playlist['id'], track_uris)
            
            return playlist['id']
        else:
            return recent_25_playlist_exists[1]

    playlist_items = create_recent_25_tracks_playlist()
    return playlist_items

@app.route('/Recent25FeaturesToDb')
def recent_25_features_to_db():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_user = sp.current_user()
    def create_data_structure():
        track_info = {}
        track_ids = []

        recent_25_playlist_id = create_recent_25_playlist()
        recent_25_playlist = sp.user_playlist(current_user['id'], recent_25_playlist_id)
        for track in recent_25_playlist['tracks']['items']:
            track_ids.append(track['track']['id'])

        tracks_features = sp.tracks(track_ids)
        audio_features = sp.audio_features(track_ids)
        print(f'Audio Features : {type(audio_features)}')
        print(f'Track Features : {type(tracks_features)}')
        # print(tracks_features['tracks'][0]['album']['name'])
        # print(tracks_features['tracks'][0]['artists'][0]['name'])

        for song in recent_25_playlist['tracks']['items']:
            song_id = song['track']['id']
            song_name = song['track']['name']

            # for track in tracks_features['tracks']:
            #     print(track['album']['name'])
            #     print(track['artists'][0]['name'])

            
            track_feature = next((track for track in tracks_features['tracks'] if track['id'] == song_id), None)
            audio_feature = next((feature for feature in audio_features if feature['id'] == song_id), None)
            
            if audio_feature:
                track_info[song_id] = {
                    'song_name' : song_name,
                    'song_id' : song_id,
                    'artist_name' : track_feature['artists'][0]['name'],
                    'album_name' : track_feature['album']['name'],
                    'acousticness' : audio_feature['acousticness'],
                    'danceability' : audio_feature['danceability'],
                    'duration_ms' : audio_feature['duration_ms'],
                    'energy' : audio_feature['energy'],
                    'instrumentalness' : audio_feature['instrumentalness'],
                    'key' : audio_feature['key'],
                    'liveness' : audio_feature['liveness'],
                    'loudness' : audio_feature['loudness'],
                    'speechiness' : audio_feature['speechiness'],
                    'tempo' : audio_feature['tempo'],
                    'time_signature' : audio_feature['time_signature']
                }
        

        return track_info
    
    def store_song_data():
        session = Session()

        track_info = create_data_structure()
        for track in track_info:
        
            new_song = AudioAnalysis(
                        song_id = track_info[track]['song_id'],
                        song_name = track_info[track]['song_name'],
                        artist_name = track_info[track]['artist_name'],
                        album_name = track_info[track]['album_name'],
                        duration_ms = track_info[track]['duration_ms'],
                        acousticness = track_info[track]['acousticness'],
                        danceability = track_info[track]['danceability'],
                        energy = track_info[track]['energy'],
                        instrumentalness = track_info[track]['instrumentalness'],
                        key = track_info[track]['key'],
                        liveness = track_info[track]['liveness'],
                        loudness = track_info[track]['loudness'],
                        speechiness = track_info[track]['speechiness'],
                        tempo = track_info[track]['tempo'],
                        time_signature = track_info[track]['time_signature'],
                        currently_playing = False
                    )
            try:
                session.add(new_song)
                session.commit()
            
            except IntegrityError as e:
                session.rollback()
                print(f"IntegrityError: {e}")
            finally:
                session.close()
                return str('Some songs are already in the db')

        return str('Added songs to db')

    return store_song_data()
    


@app.route('/GetTrackInfo')
def GetTrackInfo():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    current_playback = sp.current_playback()

    if current_playback:
        session = Session()

        song_id = current_playback['item']['id']

        if not session.query(AudioAnalysis).filter(AudioAnalysis.song_id == song_id).first():

            song_name = current_playback['item']['name']
            album_name = current_playback['item']['album']['name']
            artist_name = current_playback['item']['artists'][0]['name']
            audio_feature = sp.audio_features(song_id)
            audio_feature = audio_feature[0]

            track_info = {
                    'song_name' : song_name,
                    'album_name' : album_name,
                    'artist_name' : artist_name,
                    'song_id' : song_id,
                    'acousticness' : audio_feature['acousticness'],
                    'danceability' : audio_feature['danceability'],
                    'duration_ms' : audio_feature['duration_ms'],
                    'energy' : audio_feature['energy'],
                    'instrumentalness' : audio_feature['instrumentalness'],
                    'key' : audio_feature['key'],
                    'liveness' : audio_feature['liveness'],
                    'loudness' : audio_feature['loudness'],
                    'speechiness' : audio_feature['speechiness'],
                    'tempo' : audio_feature['tempo'],
                    'time_signature' : audio_feature['time_signature']
                }           

            try:
                currently_playing_songs = session.query(AudioAnalysis).filter(AudioAnalysis.currently_playing == True).all()
                if currently_playing_songs:
                    for song in currently_playing_songs:
                        song.currently_playing = False

                
                new_song = AudioAnalysis(
                    song_id = track_info['song_id'],
                    song_name = track_info['song_name'],
                    artist_name = track_info['artist_name'],
                    album_name = track_info['album_name'],
                    acousticness = track_info['acousticness'],
                    danceability = track_info['danceability'],
                    duration_ms = track_info['duration_ms'], 
                    energy = track_info['energy'],
                    instrumentalness = track_info['instrumentalness'],
                    key = track_info['key'],
                    liveness = track_info['liveness'],
                    loudness = track_info['loudness'],
                    speechiness = track_info['speechiness'],
                    tempo = track_info['tempo'],
                    time_signature = track_info['time_signature'],
                    currently_playing = True
                )

                session.add(new_song)
                session.commit()

                print(str(f"Song: {track_info['song_name']} Album: {track_info['album_name']} Artist: {track_info['artist_name']} Length: {int(track_info['duration_ms']) / 1000} seconds"))

                length = int(track_info['duration_ms'])
                progress = int(current_playback['progress_ms'])
                sleep_time = (length - progress) / 1000

                session.close()

                time.sleep(sleep_time + 2.5)
                return redirect(url_for('GetTrackInfo', _external = True))
            
            except IntegrityError as e:
                print(f"IntegrityError: {e}")
                session.rollback()
                return jsonify({'error': 'A song with the same song_id already exists in the database'})

            except Exception as e:
                print(f"Error: {e}")
                session.rollback()
                return jsonify({'error': 'An error occurred while adding the song to the database'})
        else:
            song_id = current_playback['item']['id']
            length = int(current_playback['item']['duration_ms'])
            progress = int(current_playback['progress_ms'])
            sleep_time = (length - progress) / 1000
            
            print(f'Song already in Database waiting {sleep_time} seconds until the next song starts.')
            time.sleep(sleep_time + 2.5)
            return redirect(url_for('GetTrackInfo', _external = True))


    else:
        time.sleep(10)
        print('Nothing is currently playing')
        return redirect(url_for('GetTrackInfo', _external = True))

@app.route('/AlbumsWorthListeingTo')
def albums_worth_listening_to():
    try:
        token_info = get_token()
    except:
        print('User not logged in')
        return redirect('/')
    
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    # Store the ids for the users top 50 artists
    top_50_artist_ids = []
    top_50_artists = sp.current_user_top_artists(limit=50, offset=0, time_range='medium_term')
    for id in top_50_artists['items']:
        top_50_artist_ids.append(id['id'])
    
    #for each artist id store their top 2 albums
    albums_worth_listening_to = {}
    for artist in top_50_artist_ids:
        albums = sp.artist_albums(artist, album_type='album', limit=2)
        for album in albums['items']:
            albums_worth_listening_to[album['artists'][0]['name']] = album['name']
        

    return albums_worth_listening_to

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
                        scope = 'playlist-read-private playlist-read-collaborative user-read-private user-read-currently-playing user-read-playback-state user-library-read playlist-modify-private user-top-read user-read-recently-played'
                        )
def handle_error(e):
    return jsonify(error=str(e)), 500