import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect
import time
import private

app = Flask(__name__)
app.config['SESSION_COOKIE_NAME'] = 'SPOTIFY COOKIE'
app.secret_key = private.SECRET_KEY
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
    

    lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.artist_top_tracks(lz_uri)

    return results['tracks'][0]['name']
    

client_id = private.CLIENT_ID
client_secret = private.CLIENT_SECRET

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
                        scope = 'user-library-read user-read-currently-playing user-top-read'
                        )


if __name__ == "__main__":
    app.run(debug=True)