from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import logging
import os
from cryptography.hazmat.primitives.asymmetric import rsa

logger = logging.getLogger("TODO: Set logger name here")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("service.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

SRC_FOLDER = os.path.dirname(os.path.abspath(__file__))
SERVICE_FOLDER = os.path.dirname(SRC_FOLDER)
INSTANCE_FOLDER = os.path.join(SERVICE_FOLDER, 'instance')
UPLOAD_FOLDER = os.path.join(INSTANCE_FOLDER, 'uploads')



db = SQLAlchemy()
DB_NAME = "database.db"
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_NAME}"
SECRET_KEY = 'hjshjhdjah kjshkjdhjs'
UPLOAD_FOLDER = '/uploads'




def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
    app.config['FULL_IMAGE_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'full')
    app.config['LOSSY_IMAGE_UPLOADS'] = os.path.join(UPLOAD_FOLDER, 'lossy')
    app.config['ALLOWED_EXTENSIONS'] = {'PNG'}
    app.config['NAME'] = 'master'
    app.config['RSA_KEY'] = rsa.generate_private_key(public_exponent=65537, key_size=4096)
    print("App root Path: ", app.root_path)
    db.init_app(app)

    from .views import views
    from .auth import auth
    from .user_profile import user_profile

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(user_profile, url_prefix='/')

    from .models import User, ENOFT
    
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')
