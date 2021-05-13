# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

# map packages
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd
import folium

# stdlib
from datetime import datetime
import os

from .artist.client import ArtistClient
from .map.client import MapClient

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()
map_client = MapClient()
artist_client = ArtistClient(map_client.pd_table)

from .routes import main
from.users.routes import users
from .artist.routes import artists

SECRET_KEY = b'\x020;yr\x21\x81\xbe"\x9d\xc1\x14\x51\xadf\xec'

app = Flask(__name__)

app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")

db.init_app(app)
login_manager.init_app(app)
bcrypt.init_app(app)

# REGISTER BLUEPRINTS HERE
app.register_blueprint(main)
app.register_blueprint(users)
app.register_blueprint(artists)

map_client.save_html(map_client.basic_map, "basic_map.html")
map_client.save_html(map_client.heat_map, "heat_map.html")

login_manager.login_view = "users.login"