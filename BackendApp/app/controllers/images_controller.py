from flask import Blueprint, jsonify, request
from app import logger, app, socketio, db
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import make_response, send_file
from ..models import GenericResponse
from ..services import UserService, ImageService, WorkerService
from ..utils import object_to_dict
import json
import os

images_controller = Blueprint('images_controller', __name__, url_prefix='/api/images')
user_service = UserService(db)
image_service = ImageService(db)
worker_service = WorkerService(db)


@images_controller.route('/upload', methods=['POST'])
@jwt_required()
def upload_image():
    # getting user id from jwt instead of request
    user_data = get_jwt_identity()
    image = request.files['image']
    model = request.form['model']
    result = image_service.save_image(image, model, user_data['id'])
    if result.success:
        worker_service.generate_projection(result.data.id)
    return make_response(jsonify(object_to_dict(result)), result.code)

@images_controller.route('/pca', methods=['POST'])
@jwt_required()
def pca():
    # getting user id from jwt instead of request
    user_data = get_jwt_identity()
    image_id = request.json.get('imageId')
    interpolation_steps = request.json.get('interpolationSteps')
    latent_edits = request.json.get('latentEdits')
    event_id = request.json.get('eventId')
    result = worker_service.run_pca(image_id, interpolation_steps, latent_edits, event_id)
    return make_response(jsonify(object_to_dict(result)), result.code)


@images_controller.route('/generateRandom', methods=['POST'])
@jwt_required()
def generate_random():
    # getting user id from jwt instead of request
    user_data = get_jwt_identity()
    model = request.json.get('model')
    number_of_images = request.json.get('numberOfImages')
    user_id = request.json.get('userId')
    event_id = request.json.get('eventId')
    result = worker_service.generate_random_images(model, number_of_images, user_id, event_id)
    return make_response(jsonify(object_to_dict(result)), result.code)


@images_controller.route('/generated/<int:image_id>/<int:index>', methods=['GET'])
@jwt_required()
def get_generated(image_id, index):
    user_data = get_jwt_identity()
    user_id = user_data['id']

    # Get the image from the database
    result = image_service.get_image_by_id(image_id)

    if not result.success:
        return make_response(jsonify(object_to_dict(result)), result.code)

    # If the image does not exist or does not belong to the user, return a 401 error
    if result.data is None or result.data.user_id != user_id:
        return make_response(object_to_dict(GenericResponse(errors=['User is not authorized to see this resource'], code=401)), 401)

    result = image_service.get_generated_image(image_id, index)

    if result.success == True:
        return send_file(result.data['image_path'], mimetype=result.data['mime_type'])
    return make_response(object_to_dict(result), result.code)


@images_controller.route('/list', methods=['GET'])
@jwt_required()
def list_images():
    user_data = get_jwt_identity()
    result = image_service.get_images_by_user(user_data['id'])
    return make_response(jsonify(object_to_dict(result)), result.code)

@images_controller.route('/image/<int:image_id>', methods=['GET'])
@jwt_required()
def get_image(image_id):
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

@images_controller.route('/image/<int:image_id>', methods=['DELETE'])
@jwt_required()
def delete_image(image_id):
    print("llamando a delete")
    user_data = get_jwt_identity()
    user_id = user_data['id']

    # Get the image from the database
    result = image_service.get_image_by_id(image_id)

    if not result.success:
        return make_response(jsonify(object_to_dict(result)), result.code)
    
    # If the image does not exist or does not belong to the user, return a 401 error
    if result.data is None or result.data.user_id != user_id:
        return make_response(object_to_dict(GenericResponse(errors=['User is not authorized to see this resource'], code=401)), 401)
    
    # Otherwise, proceed to delete the image
    result = image_service.delete_image(image_id)
    return make_response(object_to_dict(result), result.code)
