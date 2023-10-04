from flask import Flask
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with 
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class SongModel(db.Model):
    id = db.Column(db.String, primary_key = True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    album_name = db.Column(db.String(100), nullable=False)
    length = db.Column(db.Integer, nullable=False)


    def __repr__(self):
        return f'Song(name={self.song_name}, artist={self.artist_name}, album = {self.album_name}, length = {self.length} milliseconds)'


song_put_args = reqparse.RequestParser()
song_put_args.add_argument("id", type=str, help="song id")
song_put_args.add_argument("song_name", type = str, help="name of song")
song_put_args.add_argument("artist_name", type = str, help="artist of song")
song_put_args.add_argument("album_name", type = str, help="album of song")
song_put_args.add_argument("length", type = int, help="length of song")

resource_fields = {
    'id': fields.String,
    'song_name': fields.String,
    'artist_name': fields.String,
    'album_name': fields.String,
    'length': fields.Integer
}
class get_song(Resource):

    @marshal_with(resource_fields)
    def get(self, id):
        result = SongModel.query.get(id=id)
        return result

class add_song(Resource):

    @marshal_with(resource_fields)
    def put(self, id):
        args = song_put_args.parse_args()
        song = SongModel(id=args['id'], song_name=args['song_name'], artist_name=args['artist_name'], album_name=args['album_name'], length=args['length'])
        db.session.add(song)
        db.session.commit()
        return song, 201
    

api.add_resource(get_song, "/song/get/<string:id>")
api.add_resource(add_song, "/song/add/<string:id>")

def handle_error(e):
    return jsonify(error=str(e)), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)