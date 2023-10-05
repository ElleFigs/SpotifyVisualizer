from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import sessionmaker
from flask_restful import Api
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
with app.app_context():
    Session = sessionmaker(bind=db.engine)
api = Api(app)



if __name__ == "__main__":
    from models import *
    from resources import *
    from routes import *
    with app.app_context():
        db.create_all()
    app.run(debug=True)