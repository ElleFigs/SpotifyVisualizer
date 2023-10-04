# Goal: when I start the server, it will store information on a database about what song I am currently playing.
# I will be able to call a get method to that database from another script to see the same now-playing data.

# Imports
import spotipy
import time
import private
import requests
import json
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with 
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask and database

app = Flask(__name__)
api = Api(app)
app.config['SESSION_COOKIE_NAME'] = 'SPOTIFY COOKIE'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = private.SECRET_KEY

TOKEN_INFO = 'TOKEN_INFO'
client_id = private.CLIENT_ID
client_secret = private.CLIENT_SECRET

db = SQLAlchemy(app)

# Initialize the model for the database. In this case we define a class and pass in the db created above.
# The class has 4 variables associated with the columns of the database.
# it also has a method to return a string with the information

class SongModel(db.Model):
    id = db.Column(db.String, primary_key = True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=True)
    album_name = db.Column(db.String(100), nullable=True)
    length = db.Column(db.String, nullable=False)
    currently_playing = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'Song(name={self.song_name}, artist={self.artist_name}, album = {self.album_name}, length = {self.length} milliseconds, currently playing = {self.currently_playing})'

#  Here we create some data to be used in another class to help interact with the db.
# first we use the reqparse library to create a flask object that will contain the arguments we will pass through later to the db
# second we create a dictionary call resource_fields and use that to tell the http response how to serialize the response

song_put_args = reqparse.RequestParser()
song_put_args.add_argument("id", type = str, help = "spotify song id")
song_put_args.add_argument("song_name", type = str, help="name of song")
song_put_args.add_argument("artist_name", type = str, help="artist of song")
song_put_args.add_argument("album_name", type = str, help="album of song")
song_put_args.add_argument("length", type = str, help="length of song")
song_put_args.add_argument("currently_playing", type = bool, help="whether a  wsong is currently playing")


resource_fields = {
    'id': fields.String,
    'song_name': fields.String,
    'artist_name': fields.String,
    'album_name': fields.String,
    'length': fields.String,
    'currently_playing': fields.Boolean
}

# Now a new class for song is created. Within this class we will define the GET, PUT, and DELETE methods for our API
class add_song(Resource):
    @marshal_with(resource_fields)
    def put(self):
        args = song_put_args.parse_args()
        with app.app_context():
            with db.session() as session:
                new_song = SongModel(id=args['id'], song_name=args['song_name'], artist_name=args['artist_name'], album_name=args['album_name'], length=args['length'], currently_playing=args['currently_playing'])
                previous_song = SongModel.query.filter_by(currently_playing=True).first()
                if previous_song: previous_song.currently_playing = False
                db.session.add(new_song)
                db.session.commit()

        return new_song, 201

class get_song(Resource):

    @marshal_with(resource_fields)
    def get(self, song_id):
        with app.app_context():
                with db.session() as session:
                    result = SongModel.query.get(id=song_id)
        return result
    
# here we add an endpoints for the song class
api.add_resource(add_song, "/song/add/")
api.add_resource(get_song, "/song/info/<int:id>")

# Here we start to create some routes for the flask server
# The first is the default landing page for this app. It will try to get a new link to an OAuth portal. In the future this link might change to be more specific.
# We then create a redirect route which will handle the getting the token_info for our user
# Finally we have a route for getting song information.
# Right now that will run automatically once authorization has cleared.

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
if __name__ == "__main__":
    with app.app_context():
            db.create_all()
    app.run(debug=True)
