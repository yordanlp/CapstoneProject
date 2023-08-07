import mimetypes
from ..models import User, GenericResponse, Image
from ..utils import *
from app import logger, app
import os
import uuid
import imghdr

class ImageService:

    def __init__(self, db) -> None:
        self.db = db

    def save_image(self, image, model, user_id) -> GenericResponse:
        try:                
            file_extension = imghdr.what(image)
            if not file_extension:
                return GenericResponse(errors=['The file uploaded is not an image'])
            image_name = uuid.uuid4().hex + '.' + file_extension
            new_image = Image(name=image_name, user_id=user_id, mime_type=image.mimetype, model=model)
            self.db.session.add(new_image)
            image.save(os.path.join(app.config['IMAGES_FOLDER'], image_name))
            self.db.session.commit()
            return GenericResponse(data=new_image)
        except Exception as e:      
            logger.error("An error has ocurred while saving the image")
            logger.error(str(e))
            return GenericResponse(code=500)

    def get_images_by_user(self, user_id):
        try:                
            images = Image.query.filter_by(user_id=user_id).all()
            return GenericResponse(data=images)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the images for user {user_id}")
            logger.error(str(e))
            return GenericResponse(code=500)
        
    def get_image_by_id(self, image_id) -> GenericResponse:
        try:                
            image = Image.query.get(image_id)
            if image is None:
                return GenericResponse(errors=['Image not found'], code=404)
            return GenericResponse(data=image)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the image {image_id}")
            logger.error(str(e))
            return GenericResponse(code=500)
        
    def get_image_by_name(self, name) -> GenericResponse:
        try:                
            image = Image.query.filter_by(name=name).first()
            if image is None:
                return GenericResponse(errors=['Image not found'], code=404)
            return GenericResponse(data=image)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the image {name}")
            logger.error(str(e))
            return GenericResponse(code=500)
    
    def get_generated_image( self, image_id, index ):
        try:                
            image = Image.query.get(image_id)
            if image is None:
                return GenericResponse(errors=['Image not found'], code=404)
            folder_name = image.name.split('.')[0]
            image_path = os.path.join(app.config['PCA_FOLDER'], folder_name, str(index) + '.png')
            mime_type, encoding = mimetypes.guess_type(image_path)
            return GenericResponse(data={'image_path': image_path, 'mime_type': mime_type}, code=200)
        except Exception as e:      
            logger.error(f"An error has ocurred while retrieving the image {image_id} and index {index}")
            logger.error(str(e))
            return GenericResponse(code=500)
        
    def asociate_image_to_user( self, image_name, user_id, model ):
        try:       
            new_image = Image(name=image_name, user_id=user_id, mime_type='image/jpeg', model=model, status_process='FINISH')
            self.db.session.add(new_image)
            self.db.session.commit()
            return GenericResponse(data=new_image)
        except Exception as e:      
            logger.error(f"An error has ocurred while asociating the image {image_name} to user {user_id}")
            logger.error(str(e))
            return GenericResponse(code=500)