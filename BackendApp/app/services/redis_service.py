import json

from .image_service import ImageService
from .user_service import UserService
from ..models import User, GenericResponse, Image
from ..utils import *
from app import logger, app
from ..socket import socketio
import os
import uuid
import imghdr
import threading
from pprint import pprint
import redis

user_service = UserService(db)
image_service = ImageService(db)

class RedisService:

    def __init__(self, db) -> None:
        self.db = db
        self.seen_messages = {}
        with app.app_context():
            self.redis_conn = redis.Redis(host=app.config['REDIS_HOST'], port=app.config['REDIS_PORT'])

    def listen_to_redis(self):
        with app.app_context():
            try:                
                pubsub = self.redis_conn.pubsub()
                pubsub.subscribe('worker2backend_queue')

                print("start listening to queue")
                for message in pubsub.listen():
                    try:
                        if message['type'] == 'message':
                            data = json.loads(message['data'])
                            #print(data)
                            if data['type'] != 'finish':
                                continue
                            self.process_message(data)
                    except Exception as e:
                        logger.error("An error has ocurred processing a message from redis")
                        logger.error(str(e))        
            except Exception as e:      
                logger.error("An error has ocurred trying to generate the projection of the image")
                logger.error(str(e))
                return GenericResponse(code=500)

    def process_message(self, data):
        event = data['triggerMessage']
        message_key = self.get_message_key(data)
        if data['success'] == False:
            socketio.emit(message_key, json.dumps(data))
            return
        
        if event['data']['endpoint'] == '/run_projection':
            self.process_finish_projection(data)
        if event['data']['endpoint'] == '/run_pca':
            self.process_finish_pca(data)
        if event['data']['endpoint'] == '/random_images':
            self.process_finish_random(data)
        if event['data']['endpoint'] == '/run_superresolution':
            self.process_finish_superresolution(data)
    
    def process_finish_pca(self, data):
        print("FINISH PCA")
        message_key = self.get_message_key(data)
        socketio.emit(message_key, json.dumps(data))

    def process_finish_projection(self, data):
        message_key = self.get_message_key(data)
        image_name = data['triggerMessage']['data']['image_id']
        result = image_service.get_image_by_name(image_name)
        if result.success != True:
            print(result.errors)
            socketio.emit(message_key, json.dumps(data))
            return

        image = result.data
        if data['success'] == False:
            image.status_process = 'ERROR'
        else:
            image.status_process = 'FINISH'

        self.db.session.commit()
        socketio.emit(message_key, json.dumps(data))

    def process_finish_superresolution(self, data):
        message_key = self.get_message_key(data)
        image_name = data['triggerMessage']['data']['image_id']
        result = image_service.get_saved_image_by_name(image_name)
        if result.success != True:
            print(result.errors)
            socketio.emit(message_key, json.dumps(data))
            return
        image = result.data
        if data['success'] == False:
            image.status_superresolution = 'ERROR'
        else:
            image.status_superresolution = 'FINISH'
        self.db.session.commit()
        socketio.emit(message_key, json.dumps(data))

    def process_finish_random(self, data):
        message_key = self.get_message_key(data)
        if data['success'] != True:
            logger.error("Something wrong happened when generating the random images")
            logger.error(data['message'])
            print("Something wrong happened when generating the random images")
            print(data['message'])
            socketio.emit(message_key, json.dumps(data))
        
        for i in data['triggerMessage']['data']['images_names']:
            image_service.asociate_image_to_user(i + '.png', data['userId'], data['triggerMessage']['data']['model'])

        socketio.emit(message_key, json.dumps(data))

    def get_message_key(self, data) -> str:
        event = data['triggerMessage']
        user_id = event['userId']
        event_id = event['eventId']
        message_key = f"{user_id}:{event_id}"
        return message_key
