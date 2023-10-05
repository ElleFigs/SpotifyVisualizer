import private

class Config:
    SECRET_KEY = private.SECRET_KEY
    SESSION_COOKIE_NAME = 'SPOTIFY COOKIE'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
