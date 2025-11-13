import os

SECRET_KEY = 'secret-key'

# SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:CaT2012!@localhost:3306/lab6' dell
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:1704@localhost:3306/lab6'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 
    '..',
    'media', 
    'images'
)
