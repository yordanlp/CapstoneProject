from ..models import User


class UserService:

    def __init__(self, db) -> None:
        self.db = db

    def create_user(self, username, email, password) -> User:
        # Check if the user already exists
        existing_user = User.query.filter_by(user_name=email).first()
        if existing_user:
            return None, 'Username already exists'

        # Create a new user
        new_user = User(user_name=username, email=email, password=password)
        self.db.session.add(new_user)
        self.db.session.commit()

        return new_user, 'User registered successfully'


    def find_user_by_email(self, email) -> User:
        return User.query.filter_by(email=email).first()


    def authenticate_user(self, email, password) -> User:
        user = self.find_user_by_email(email)
        if user and user.password == password:
            return user
        return None


    def get_user_by_id(self, user_id) -> User:
        return User.query.get(user_id)