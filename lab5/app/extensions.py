from .db import DBConnector
from flask_login import LoginManager

db = DBConnector()
login_manager = LoginManager()