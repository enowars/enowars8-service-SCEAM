from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from . import db, logger  # means from __init__.py import db
from flask_login import login_required, current_user
from .models import ENOFT
import random
import string
import os
from flask import current_app
import cryptography
import datetime
from PIL import Image
from cryptography.hazmat.primitives import hashes
import base64
import io
from cryptography.hazmat.primitives import serialization

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
        img = Image.open(file)
        img.verify()
        img = Image.open(file)
    except Exception as e:
        print(e)
        flash('Invalid image')
        return render_template("create_enoft.html", user=current_user)

    if img.format not in current_app.config['ALLOWED_EXTENSIONS']:
        flash('Invalid image format')
        return render_template("create_enoft.html", user=current_user)

    upload_handler(img)
    img.close()

    return redirect(url_for('user_profile.profile'))


def upload_handler(img):
    all_file_names = [f.image_path for f in ENOFT.query.all()]
    file_name = ''.join(
        random.choices(
            string.ascii_uppercase + string.digits,
            k=20)) + '.png'

    # force unique filenames
    while file_name in all_file_names:
        file_name = ''.join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=20)) + '.png'

    full_save_path = os.path.join(
        current_app.config["FULL_IMAGE_UPLOADS"], file_name)
    lossy_save_path = os.path.join(
        current_app.config["LOSSY_IMAGE_UPLOADS"], file_name)
    certificate = build_cert(img)

    img.save(full_save_path)
    new_enoft = ENOFT(image_path=file_name,
                      certificate=certificate, user_id=current_user.id)
    db.session.add(new_enoft)
    db.session.commit()

    # TODO generate lossy image from full image
    img.save(lossy_save_path)

    flash('File uploaded successfully')


def build_cert(img):
    owner_name = current_user.name + " <" + current_user.email + ">"
    time = datetime.datetime.now()
    fake_location = io.BytesIO()
    img.save(fake_location, format='PNG')
    readable_hash = hashes.Hash(hashes.MD5())
    readable_hash.update(fake_location.getvalue())
    readable_hash = readable_hash.finalize()
    identifier = cryptography.x509.ObjectIdentifier("1.3.6.1.4.1.69420.1.1")
    public_key = current_user.public_key
    public_key = serialization.load_pem_public_key(
        public_key.encode(), backend=cryptography.hazmat.backends.default_backend())
    unrecognized_extension = cryptography.x509.UnrecognizedExtension(
        oid=identifier, value=readable_hash)

    cert = cryptography.x509.CertificateBuilder()
    cert = cert.subject_name(cryptography.x509.Name([cryptography.x509.NameAttribute(
        cryptography.x509.oid.NameOID.COMMON_NAME, owner_name), ]))
    cert = cert.issuer_name(cryptography.x509.Name([cryptography.x509.NameAttribute(
        cryptography.x509.oid.NameOID.COMMON_NAME, current_app.config['NAME'])]))
    cert = cert.public_key(public_key)
    cert = cert.serial_number(cryptography.x509.random_serial_number())
    cert = cert.not_valid_before(time)
    cert = cert.not_valid_after(time + datetime.timedelta(days=1))
    cert = cert.add_extension(unrecognized_extension, critical=False)
    cert = cert.sign(
        current_app.config['RSA_KEY'],
        cryptography.hazmat.primitives.hashes.SHA512())

    pem_cert = cert.public_bytes(encoding=serialization.Encoding.PEM)
    base64_cert = base64.b64encode(pem_cert)
    return base64_cert
