from flask import Blueprint, request
from app import logger

#from app.services.user_service import UserService

user_controller = Blueprint('user_controller', __name__, url_prefix='/users')
#user_service = UserService()

@user_controller.route('/', methods=['GET'])
def list_users():
    logger.debug("This is a log message")
    return "Hello World"