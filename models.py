from app import db

class SongModel(db.Model):
    song_id = db.Column(db.String, primary_key = True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=True)
    album_name = db.Column(db.String(100), nullable=True)
    length = db.Column(db.String, nullable=False)
    currently_playing = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'Song(name={self.song_name}, artist={self.artist_name}, album = {self.album_name}, length = {self.length} milliseconds, currently playing = {self.currently_playing})'
