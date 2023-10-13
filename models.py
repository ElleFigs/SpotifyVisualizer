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

class AudioAnalysis(db.Model):
    song_id = db.Column(db.String, primary_key = True)
    song_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    album_name = db.Column(db.String(100), nullable=False)
    acousticness = db.Column(db.Float, nullable=False)
    danceability = db.Column(db.Float, nullable=False)
    duration_ms = db.Column(db.Float, nullable=False) 
    energy = db.Column(db.Float, nullable=False)
    instrumentalness = db.Column(db.Float, nullable=False)
    key = db.Column(db.Integer, nullable=False)
    liveness = db.Column(db.Float, nullable=False)
    loudness = db.Column(db.Float, nullable=False)
    speechiness = db.Column(db.Float, nullable=False)
    tempo = db.Column(db.Float, nullable=False)
    time_signature = db.Column(db.Integer, nullable=False)
    currently_playing = db.Column(db.Boolean, nullable=False)
    