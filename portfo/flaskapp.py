import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__)                                  # L1
app.config.from_object(Config)
db = SQLAlchemy(app)