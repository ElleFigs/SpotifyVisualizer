from flask_restful import reqparse, fields, marshal_with
from app import api

song_put_args = reqparse.RequestParser()
song_put_args.add_argument("id", type = str, help = "spotify song id")
song_put_args.add_argument("song_name", type = str, help="name of song")
song_put_args.add_argument("artist_name", type = str, help="artist of song")
song_put_args.add_argument("album_name", type = str, help="album of song")
song_put_args.add_argument("length", type = str, help="length of song")
song_put_args.add_argument("currently_playing", type = bool, help="whether a song is currently playing")

resource_fields = {
    'id': fields.String,
    'song_name': fields.String,
    'artist_name': fields.String,
    'album_name': fields.String,
    'length': fields.String,
    'currently_playing': fields.Boolean
}

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