from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DEBUG = os.getenv('DEBUG')
    SECRET_KEY = 'my-secret-key'
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    IMAGES_FOLDER = os.getenv("IMAGES_FOLDER")
    PCA_FOLDER = os.getenv("PCA_FOLDER")
    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")