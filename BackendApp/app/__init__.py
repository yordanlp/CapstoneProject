from flask import Flask
from config import Config
import logging, os

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

# Import the controllers and register the blueprints
from app.controllers.user_controller import user_controller
app.register_blueprint(user_controller)