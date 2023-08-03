import json
import threading
from flask import Flask
import logging, os
from .configuration import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS, cross_origin
#from flask_socketio import SocketIO
from .socket import socketio
import redis


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

# Load the configuration from config.py
app.config.from_object(Config)

#adding cors
cors = CORS(app, origins='*')

#JWT
jwt = JWTManager(app)

#Database related
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#redis
redis_conn = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

from .models import *


# Import the controllers and register the blueprints
from app.controllers.user_controller import user_controller
from app.controllers.images_controller import images_controller
app.register_blueprint(user_controller)
app.register_blueprint(images_controller)


#setting up socket io
#socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True)
socketio.init_app(app)

# start a new thread that listens to Redis
from .services import RedisService
redis_service = RedisService(db)
if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
    print("CREANDO THREAD")
    t = threading.Thread(target=redis_service.listen_to_redis)
    t.start()