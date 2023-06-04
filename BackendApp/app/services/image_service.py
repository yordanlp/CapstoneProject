from ..models import User, GenericResponse, Image
from ..utils import *
from app import logger, app
import os
import uuid
import imghdr

class ImageService:

    def __init__(self, db) -> None:
        self.db = db

    def save_image(self, image, user_id) -> GenericResponse:
        try:                
            file_extension = imghdr.what(image)
            if not file_extension:
                return GenericResponse(errors=['The file uploaded is not an image'])
            image_name = uuid.uuid4().hex
            new_image = Image(name=image_name, user_id=user_id, mime_type=image.mimetype)
            self.db.session.add(new_image)
            image.save(os.path.join(app.config['IMAGES_FOLDER'], image_name))
            self.db.session.commit()
            return GenericResponse(data=new_image)
        except Exception as e:      
            logger.error("An error has ocurred while saving the image")
            logger.error(str(e))
            return GenericResponse(500)

    def get_images_by_user(self, user_id):
        try:                
            images = Image.query.filter_by(user_id=user_id).all()
            return GenericResponse(data=images)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the images for user {user_id}")
            logger.error(str(e))
            return GenericResponse(500)
        
    def get_image_by_id(self, image_id) -> Image:
        try:                
            image = Image.query.get(image_id)
            if image is None:
                return GenericResponse(errors=['Image not found'], code=404)
            return GenericResponse(data=image)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the image {image_id}")
            logger.error(str(e))
            return GenericResponse(500)
        