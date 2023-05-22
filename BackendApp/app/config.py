from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG')
    SECRET_KEY = 'my-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///myapp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False