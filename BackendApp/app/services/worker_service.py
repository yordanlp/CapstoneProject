import json
from .image_service import ImageService
from .user_service import UserService
from ..models import User, GenericResponse, Image
from ..utils import *
from app import logger, app, redis_conn
import os
import uuid
import imghdr

user_service = UserService(db)
image_service = ImageService(db)

class WorkerService:

    def __init__(self, db) -> None:
        self.db = db

    def generate_projection(self, image_id) -> GenericResponse:
        try:                
            result = image_service.get_image_by_id(image_id)
            if result.success != True:
                return result

            image = result.data

            model = 'alis'
            if image.model != 'alis':
                model = 'stylegan2'

            data = {
                'eventId': uuid.uuid4().hex,
                'userId': image.user_id,
                'model': model,
                'data': {
                    'endpoint': '/run_projection',
                    'image_id': image.name,
                    'model' : image.model
                }
            }
            image.status_process = 'START'
            self.db.session.commit()
            redis_conn.publish('backend2worker_queue', json.dumps(data))
            return GenericResponse(data=data, code=200)
        except Exception as e:      
            logger.error("An error has ocurred trying to generate the projection of the image")
            logger.error(str(e))
            return GenericResponse(code=500)
        
    def run_pca(self, image_id, interpolation_steps, latent_edits, event_id) -> GenericResponse:
        try:                
            result = image_service.get_image_by_id(image_id)
            print("Running PCA")
            if result.success != True:
                return result
            image = result.data
            vectorid = image.name.split('.')[0] + '.pkl'

            model = 'alis'
            if image.model != 'alis':
                model = 'stylegan2'
 
            data = {
                'eventId': event_id,
                'userId': image.user_id,
                'model': model,
                'data': {
                    "endpoint": '/run_pca',
                    "vector_id": vectorid,
                    "model": image.model,
                    "interpolation_steps": int(interpolation_steps),
                    "latent_edits": latent_edits
                }
            }
            redis_conn.publish('backend2worker_queue', json.dumps(data))
            return GenericResponse(data=data, code=200)
        except Exception as e:      
            logger.error("An error has ocurred trying to generate the projection of the image")
            logger.error(str(e))
            return GenericResponse(code=500)

        