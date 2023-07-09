from app import db
from .user import User

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    mime_type = db.Column(db.String(10))
    user = db.relationship('User', backref=db.backref('images', lazy=True))
    model = db.Column(db.String(30))
