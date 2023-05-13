from flask import Blueprint, request

#from app.services.user_service import UserService

user_controller = Blueprint('user_controller', __name__, url_prefix='/users')
#user_service = UserService()

@user_controller.route('/', methods=['GET'])
def list_users():
    return "Hello World"