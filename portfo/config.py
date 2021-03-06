"""
Contains all flask configuration
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

# from config import Config

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    """required"""
    title = 'portfo v0.1'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'lkjhkj2h34kj2l3h4lk2j34hl2k2l3kj4h'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_PATH = os.path.join(basedir, 'static', 'uploads')


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'








