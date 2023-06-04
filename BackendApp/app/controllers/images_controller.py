from flask import Blueprint, jsonify, request
from app import logger, app
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import make_response, send_file
from flask_cors import CORS, cross_origin
from ..models import User, GenericResponse
from ..services import UserService, ImageService
from ..utils import object_to_dict
from app import db
import json
import os

images_controller = Blueprint('images_controller', __name__, url_prefix='/api/images')
user_service = UserService(db)
image_service = ImageService(db)


@images_controller.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    # getting user id from jwt instead of request
    user_data = get_jwt_identity()
    image = request.files['image']
    result = image_service.save_image(image, user_data['id'])
    return make_response(jsonify(object_to_dict(result)), result.code)
    


@images_controller.route('/list', methods=['GET'])
@jwt_required()
def list_images():
    user_data = get_jwt_identity()
    result = image_service.get_images_by_user(user_data['id'])
    return make_response(jsonify(object_to_dict(result)), result.code)

@images_controller.route('/image/<int:image_id>', methods=['GET'])
@jwt_required()
def serve_image(image_id):
    user_data = get_jwt_identity()
    user_id = user_data['id']

    # Get the image from the database
    result = image_service.get_image_by_id(image_id)

    if not result.success:
        return make_response(jsonify(object_to_dict(result)), result.code)

    # If the image does not exist or does not belong to the user, return a 401 error
    if result.data is None or result.data.user_id != user_id:
        return make_response(object_to_dict(GenericResponse(errors=['User is not authorized to see this resource'], code=401)), 401)

    # Otherwise, return the image file
    image_path = os.path.join(app.config['IMAGES_FOLDER'], result.data.name)
    return send_file(image_path, mimetype=result.data.mime_type)