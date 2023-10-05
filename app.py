from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app)

if __name__ == "__main__":
    from models import SongModel
    from resources import add_song, get_song
    from routes import login, redirect_page, GetTrackInfo
    app.run(debug=True)