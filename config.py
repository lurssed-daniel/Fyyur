import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# TODO IMPLEMENT DATABASE URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost:5432/Fyyur'
