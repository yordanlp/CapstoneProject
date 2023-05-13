from flask import Flask

app = Flask(__name__)

# Load the configuration from config.py
app.config.from_object('config.Config')

# Import the controllers and register the blueprints
#from app.controllers.user_controller import user_controller
#app.register_blueprint(user_controller)