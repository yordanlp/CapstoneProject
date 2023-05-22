from flask import Blueprint, jsonify, request
from app import logger
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from ..models import User
from ..services import UserService
from app import db
import json

#from app.services.user_service import UserService

user_controller = Blueprint('user_controller', __name__, url_prefix='/users')
user_service = UserService(db)

@user_controller.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')

    # Check if the user already exists
    existing_user = user_service.find_user_by_email(email)
    if existing_user:
        return jsonify({'message': 'email already exists'}), 409

    # Create a new user
    new_user = User(user_name=username, email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


@user_controller.route('/login', methods=['POST'])
def login():
    email = request.json.get('email')
    password = request.json.get('password')
    print(email, password)

    user = user_service.authenticate_user(email, password)
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401

    access_token = create_access_token(identity={'id': user.id, 'user_name': user.user_name, 'email': user.email})
    return jsonify({'access_token': access_token}), 200


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