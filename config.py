import os
from dotenv import load_dotenv
from igdb.wrapper import IGDBWrapper

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

wrapper = IGDBWrapper(os.getenv("API_ID"), os.getenv("API_TOKEN"))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'keggy-the-keg'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    POSTS_PER_PAGE = 5

    LOGIN_DISABLED = False # For testing
    # Terminal debug command (can't set here): set FLASK_DEBUG=1