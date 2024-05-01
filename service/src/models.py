from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    public_key = db.Column(db.String(150))
    name = db.Column(db.String(150))
    enofts = db.relationship('ENOFT')
    
class ENOFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_full = db.Column(db.String(10000))
    image_lossy = db.Column(db.String(10000))
    certificate = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
