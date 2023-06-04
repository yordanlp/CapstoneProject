from flask import Blueprint, jsonify, request
from app import logger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import make_response
from flask_cors import CORS, cross_origin
from ..models import User, GenericResponse
from ..services import UserService
from ..utils import object_to_dict
from app import db
import json

user_controller = Blueprint('user_controller', __name__, url_prefix='/api/users')
user_service = UserService(db)

@user_controller.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    result = user_service.create_user(username, email, password)
    return make_response(jsonify(object_to_dict(result)) , result.code)


@user_controller.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')

    result = user_service.authenticate_user(email, password)

    if result.success == True:
        access_token = create_access_token(identity={'id': result.data.id, 'user_name': result.data.user_name, 'email': result.data.email})
        return make_response(jsonify(object_to_dict(GenericResponse(data=access_token))), 200)
    return make_response(jsonify(object_to_dict(result)), result.code)


@user_controller.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    user_data = get_jwt_identity()
    print("current_user_id", user_data)
    user = user_service.get_user_by_id(user_data['id'])
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify(user_data), 200

@user_controller.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    #jti = get_raw_jwt()['jti']
    # Implement your logic to store or invalidate the token
    # For example, you can add the token to a blacklist
    # or remove it from the client-side storage

    return jsonify({'message': 'Logged out successfully'}), 200