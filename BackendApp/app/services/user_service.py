from ..models import User, GenericResponse
from ..utils import *
from app import logger


class UserService:

    def __init__(self, db) -> None:
        self.db = db

    def create_user(self, username, email, password) -> GenericResponse:
        try:
            existing_user = self.find_user_by_email(email)
            if existing_user:
                return GenericResponse(errors=['User with that email already exists'], code=409)

            # Create a new user
            new_user = User(user_name=username, email=email, password=hash_password(password))
            self.db.session.add(new_user)
            self.db.session.commit()
            print(model_to_dict(new_user))
            return GenericResponse(data=new_user)
        except Exception as e:
            logger.error("An error has ocurred while creating the user")
            logger.error(e)
            return GenericResponse(code=500)


    def find_user_by_email(self, email) -> User:
        return User.query.filter_by(email=email).first()


    def authenticate_user(self, email, password) -> GenericResponse:
        try:
            user = self.find_user_by_email(email)
            if user and user.check_password(password):
                return GenericResponse(data=user)
            return GenericResponse(errors=['Username or password are incorrect'], code=409)
        except Exception as e:
            logger.error("An error has ocurred while authenticating the user")
            logger.error(e)
            return GenericResponse(500)

    def get_user_by_id(self, user_id) -> User:
        return User.query.get(user_id)