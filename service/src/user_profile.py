from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, logger   ##means from __init__.py import db
from flask_login import  login_required,  current_user
from .models import ENOFT
import random
import string
import os
from flask import current_app
import cryptography
import datetime
import PIL




user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template("profile.html", user=current_user)



@user_profile.route('/create_enoft', methods=['GET', 'POST'])
@login_required
def create_enoft():
    if request.method == 'GET':
        return render_template("create_enoft.html", user=current_user)
    
    if 'file' not in request.files:
        flash('No file part')
        return render_template("create_enoft.html", user=current_user)
    
    file = request.files['file']
    if not file or file.filename == '':
        flash('No selected file')
        return render_template("create_enoft.html", user=current_user)
    
    if file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
        flash('File too large')
        return render_template("create_enoft.html", user=current_user)
    
    img = None
    try:
        img = PIL.Image.open(file)
        img.verify()
    except:
        flash('Invalid image')
        return render_template("create_enoft.html", user=current_user)
    
    if img.format not in current_app.config['ALLOWED_EXTENSIONS']:
        flash('Invalid image format')
        return render_template("create_enoft.html", user=current_user)
    

    img.close()

    upload_handler(file)
    
    return redirect(url_for('user_profile.profile'))
    


def upload_handler(file):
    all_file_names = [f.image_path for f in ENOFT.query.all()]
    file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + '.png'

    # force unique filenames
    while file_name in all_file_names:
        file_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20)) + '.png'

    full_save_path = os.path.join(current_app.config["FULL_IMAGE_UPLOADS"], file_name)
    lossy_save_path = os.path.join(current_app.config["LOSSY_IMAGE_UPLOADS"], file_name)
    
    flash('File uploaded successfully')
    file.save(full_save_path)
    
    #TODO generate lossy image from full image
    
    #TODO generate certificate from full image

def build_cert(key):
    
    return  cryptography.x509.CertificateBuilder().subject_name(
        cryptography.x509.Name([
            cryptography.x509.NameAttribute(cryptography.x509.oid.NameOID.COMMON_NAME, 'test'),
        ])
    ).issuer_name(
        cryptography.x509.Name([
            cryptography.x509.NameAttribute(cryptography.x509.oid.NameOID.COMMON_NAME, current_app.config['NAME']),
        ])
    ).public_key(
        key.public_key()
    ).serial_number(
        cryptography.x509.random_serial_number()
    ).not_valid_before(
        self.time
    ).not_valid_after(
        self.time + datetime.timedelta(days=1)
    ).sign(
        key,
        cryptography.hazmat.primitives.hashes.SHA512()
    )



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
