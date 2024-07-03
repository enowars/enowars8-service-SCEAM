from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    public_key = db.Column(db.String(150))
    name = db.Column(db.String(150))
    enofts = db.relationship('ENOFT')
    quality = db.Column(db.Integer, default=1)
    vendor_lock = db.Column(db.Boolean, default=False)
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())


class ENOFT(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(10000))
    certificate = db.Column(db.String(10000))
    owner_email = db.Column(db.Integer, db.ForeignKey('user.email'))
    creation_date = db.Column(db.DateTime(timezone=True), default=func.now())
    profile_image = db.Column(db.Boolean, default=False)
    description = db.Column(db.String(10000), default='Look at my new ENOFT!')
