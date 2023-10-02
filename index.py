from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class SongModel(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    album = db.Column(db.String(100), nullable=False)
    length = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'Song(name={name}, artist={artist}, album = {album}, length = {length} seconds)'

# db.create_all()


video_put_args = reqparse.RequestParser()
video_put_args.add_argument("name", type = str, help="name of song")
video_put_args.add_argument("artist", type = str, help="artist of song")
video_put_args.add_argument("album", type = str, help="album of song")
video_put_args.add_argument("length", type = int, help="length of song")

resource_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'artist': fields.String,
    'album': fields.String,
    'length': fields.Integer
}

class song(Resource):

    @marshal_with(resource_fields)
    def get(self, song_id):
        result = SongModel.query.get(id=song_id)
        return result

    @marshal_with(resource_fields)
    def put(self, song_id):
        args = video_put_args.parse_args()
        song = SongModel(id=song_id, name=args['name'], artist=args['artist'], album=args['album'], length=args['length'])
        db.session.add(song)
        db.session.commit()
        return song, 201
    
    def delete(self, song_id):
        abort_if_song_not_in_songs(song_id)
        del songs[song_id]
        return '', 204

    

api.add_resource(song, "/song/<int:song_id>")

if __name__ == "__main__":
    app.run(debug=True)