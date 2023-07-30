import json

from .image_service import ImageService
from .user_service import UserService
from ..models import User, GenericResponse, Image
from ..utils import *
from app import logger, app, redis_conn
from ..socket import socketio
import os
import uuid
import imghdr
import threading

user_service = UserService(db)
image_service = ImageService(db)

class RedisService:

    def __init__(self, db) -> None:
        self.db = db
        self.seen_messages = {}
        self.lock = threading.Lock()

    def listen_to_redis(self):
        with app.app_context():
            try:                
                pubsub = redis_conn.pubsub()
                pubsub.subscribe('worker2backend_queue')

                print("start listening to queue")
                for message in pubsub.listen():
                    try:
                        if message['type'] == 'message':
                            data = json.loads(message['data'])
                            #print(data)
                            if data['success'] == True:
                                self.process_message(data)
                            else:
                                logger.error(data['message'])
                    except Exception as e:
                        logger.error("An error has ocurred processing a message from redis")
                        logger.error(str(e))        
            except Exception as e:      
                logger.error("An error has ocurred trying to generate the projection of the image")
                logger.error(str(e))
                return GenericResponse(code=500)

    def process_message(self, data):
        with self.lock:
            event = data['triggerMessage']
            if event is None:
                return
            user_id = event['userId']
            event_id = event['eventId']
            message_key = self.get_message_key(data)
            value_redis = redis_conn.get(message_key)
            if value_redis == None:
                value_redis = 0
            print("--------------MESSAGE KEY-------------------: " + message_key + " " + str(value_redis))
            #if  redis_conn.incr(message_key) == 1:
            #    print( f"event with used_id: {user_id} and event_id: {event_id} was already proccessed" )
            #    return
            print(event)
            if event['data']['endpoint'] == '/run_projection':
                self.process_finish_projection(data)
            if event['data']['endpoint'] == '/run_pca':
                self.process_finish_pca(data)
            if event['data']['endpoint'] == '/random_images':
                self.process_finish_random(data)
    
    def process_finish_pca(self, data):
        print("FINISH PCA")
        message_key = self.get_message_key(data)
        print(message_key)
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
        image.status_process = 'FINISH'
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
