import wat.config as config
from wat.models import db
from flask import Flask

app = Flask(__name__)
app.config["APP_NAME"] = config.APP_NAME
app.config["SQLALCHEMY_DATABASE_URI"] = config.DB_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = config.SECRET

db.app = app
db.init_app(app)

import wat.controllers
