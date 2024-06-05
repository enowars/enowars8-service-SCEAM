from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import logging
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import random

logger = logging.getLogger("ENOFT_LOGER")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("../instance/service.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

SRC_FOLDER = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SRC_FOLDER, 'uploads')


db = SQLAlchemy()
DB_NAME = "database.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
# random cookie key
SECRET_KEY = ''.join(random.choice(
    'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50))


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['FULL_IMAGE_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'full')
    app.config['LOSSY_IMAGE_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'lossy')
    app.config['ALLOWED_EXTENSIONS'] = {'PNG', 'JPG', 'JPEG', 'GIF'}
    app.config['NAME'] = 'master'
    app.config['PAGE_SIZE'] = 10
    app.config['RSA_KEY'] = rsa.generate_private_key(
        public_exponent=65537, key_size=4096)
    db.init_app(app)

    Path(app.config['FULL_IMAGE_UPLOADS']).mkdir(parents=True, exist_ok=True)
    Path(app.config['LOSSY_IMAGE_UPLOADS']).mkdir(parents=True, exist_ok=True)

    from .views import views
    from .auth import auth
    from .user_profile import user_profile

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(user_profile, url_prefix='/')

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
