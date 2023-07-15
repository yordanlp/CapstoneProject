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

class RedisService:

    def __init__(self, db) -> None:
        self.db = db
        self.seen_messages = {}

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
                            print(data)
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
        event = data['triggerMessage']
        print("event", event)
        if event is None:
            return
        user_id = event['userId']
        event_id = event['eventId']
        message_key = f"{user_id}:{event_id}"
        if  redis_conn.get(message_key) == b'True':
            print( f"event with used_id: {user_id} and event_id: {event_id} was already proccessed" )
            return
        redis_conn.set(message_key, 'True')
        print("event")
        print(event)
        if event['data']['endpoint'] == '/run_projection':
            self.process_finish_projection(event['data'])
    
    def process_finish_projection(self, data):
        image_name = data['image_id']
        print(image_name)
        result = image_service.get_image_by_name(image_name)
        if result.success != True:
            print(result.errors)
            return
        image = result.data
        image.status_process = 'FINISH'
        self.db.session.commit()
