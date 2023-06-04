from flask import Flask
import logging, os
from .configuration import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin


log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logs')
if not os.path.exists(log_dir):
    os.mkdir(log_dir)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join(log_dir, 'CapstoneBE.log'))
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app = Flask(__name__)

#adding cors
cors = CORS(app, origins='*')

# Load the configuration from config.py
app.config.from_object(Config)

#JWT
jwt = JWTManager(app)

#Database related
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from .models import *


# Import the controllers and register the blueprints
from app.controllers.user_controller import user_controller
from app.controllers.images_controller import images_controller
app.register_blueprint(user_controller)
app.register_blueprint(images_controller)
