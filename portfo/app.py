"""
Contains all flask configuration
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required

from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'