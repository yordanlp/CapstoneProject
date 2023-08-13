from app import db
from .user import User

class SavedImage(db.Model):
    __tablename__ = 'saved_images'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref=db.backref('saved_images', lazy=True))
    parent_image_id = db.Column(db.Integer, db.ForeignKey('images.id'))
    parent_image = db.relationship('Image', backref=db.backref('saved_images', lazy=True))
    status_superresolution = db.Column(db.String(30))
