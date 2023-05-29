from ..models import User, GenericResponse
from flask import jsonify
from ..utils import *


class UserService:

    def __init__(self, db) -> None:
        self.db = db

    def create_user(self, username, email, password) -> GenericResponse:
        try:
            existing_user = self.find_user_by_email(email)
            if existing_user:
                return GenericResponse(errors=['User with that email already exists'])

            # Create a new user
            new_user = User(user_name=username, email=email, password=password)
            self.db.session.add(new_user)
            self.db.session.commit()
            print(model_to_dict(new_user))
            return GenericResponse(data=new_user)
        except Exception as e:
            return GenericResponse(errors=[str(e)])


    def find_user_by_email(self, email) -> User:
        return User.query.filter_by(email=email).first()


    def authenticate_user(self, email, password) -> GenericResponse:
        try:
            user = self.find_user_by_email(email)
            if user and user.password == password:
                return GenericResponse(data=user)
            return GenericResponse(errors=['Username or password are incorrect'])
        except Exception as e:
            return GenericResponse(errors=[str(e)])


    def get_user_by_id(self, user_id) -> User:
        return User.query.get(user_id)