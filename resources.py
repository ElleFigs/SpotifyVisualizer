from flask import session
from flask_restful import reqparse, fields, marshal_with, Resource
from sqlalchemy import func
from app import app, api, db, Session
from models import *
import random

song_put_args = reqparse.RequestParser()
song_put_args.add_argument("song_id", type = str, help = "spotify song id")
song_put_args.add_argument("song_name", type = str, help="name of song")
song_put_args.add_argument("artist_name", type = str, help="artist of song")
song_put_args.add_argument("album_name", type = str, help="album of song")
song_put_args.add_argument("length", type = str, help="length of song")
song_put_args.add_argument("currently_playing", type = bool, help="whether a song is currently playing")

resource_fields = {
    'song_id': fields.String,
    'song_name': fields.String,
    'artist_name': fields.String,
    'album_name': fields.String,
    'length': fields.String,
    'currently_playing': fields.Boolean
}

analysis_fields = {
    'song_id' : fields.String,
    'song_name' : fields.String,
    'artist_name' : fields.String,
    'album_name' : fields.String,
    'acousticness' : fields.Float,
    'danceability' : fields.Float,
    'duration_ms' :  fields.Float,
    'energy' : fields.Float,
    'instrumentalness' : fields.Float,
    'key' : fields.Integer,
    'liveness' : fields.Float,
    'loudness' : fields.Float,
    'speechiness' : fields.Float,
    'tempo' : fields.Float,
    'time_signature' : fields.Integer
}

class add_song(Resource):
    @marshal_with(resource_fields)
    def put(self):
        args = song_put_args.parse_args()
        session = Session()
        with app.app_context():
            with db.session() as session:
                new_song = SongModel(song_id=args['song_id'], song_name=args['song_name'], artist_name=args['artist_name'], album_name=args['album_name'], length=args['length'], currently_playing=args['currently_playing'])
                previous_songs = SongModel.query.filter_by(currently_playing=True).all()
                if previous_songs: 
                    for song in previous_songs:
                        song.currently_playing = False
                db.session.add(new_song)
                db.session.commit()
            session.close()
        return new_song, 201

class get_song(Resource):

    @marshal_with(resource_fields)
    def get(self, song_id):
        session = Session()
        with app.app_context():
                with db.session() as session:
                    result = SongModel.query.get(song_id)
                session.close()
        return result

class get_currently_playing(Resource):
     @marshal_with(analysis_fields)
     def get(self):
        session = Session()
        with app.app_context():
            with db.session() as session:
                result = AudioAnalysis.query.filter(AudioAnalysis.currently_playing==True).first()
            session.close()
        return result
     
class get_25_recent_song_features(Resource):
    @marshal_with(analysis_fields)
    def get(self):
        session = Session()
        with app.app_context():
                with db.session() as session:
                    result = AudioAnalysis.query.order_by(func.random()).limit(5).all()
                    
                session.close()
        return result
    
# here we add an endpoints for the song class
api.add_resource(add_song, "/song/add/")
api.add_resource(get_song, "/song/info/<string:song_id>")
api.add_resource(get_currently_playing, "/song/currentlyplaying/")
api.add_resource(get_25_recent_song_features, "/song/recent/")