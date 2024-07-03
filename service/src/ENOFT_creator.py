from flask import request, flash, current_app
from cryptography.hazmat.primitives import hashes, serialization
from flask_login import current_user
from . import db
from .models import ENOFT
from PIL import Image
import random
import string
import os
import cryptography
import datetime
import base64
import io


class ENOFT_creator:

    def __init__(self) -> None:
        self.valid = True
        self.verify_file()
        self.handle_upload()

    def shortcuircuit(foo):
        def check(self):
            if not self.valid:
                return
            foo(self)
        return check

    def verify_file(self):
        self.check_file_existence()
        self.check_file_name()
        self.check_file_size()
        self.check_image()

    @shortcuircuit
    def check_file_existence(self):
        if 'file' not in request.files:
            flash('No file part', 'error')
            self.valid = False

    @shortcuircuit
    def check_file_name(self):
        self.file = request.files['file']
        if not self.file or self.file.filename == '':
            flash('No selected file', 'error')
            self.valid = False

    @shortcuircuit
    def check_file_size(self):
        if self.file.content_length > current_app.config['MAX_CONTENT_LENGTH']:
            flash('File too large', 'error')
            self.valid = False

    @shortcuircuit
    def check_image(self):
        img = None
        try:
            img = Image.open(self.file)
            img.verify()
            self.img = Image.open(self.file)
        except:
            flash('Invalid image', 'error')
            self.valid = False

    @shortcuircuit
    def check_image_format(self):
        if self.img.format not in current_app.config['ALLOWED_EXTENSIONS']:
            flash('Invalid image format', 'error')
            self.valid = False

    @shortcuircuit
    def handle_upload(self):
        file_name = generate_unique_filename()
        full_save_path = os.path.join(
            current_app.config["FULL_IMAGE_UPLOADS"], file_name)
        certificate = build_cert(self.img)
        self.img.save(full_save_path)
        description = 'Look at my new ENOFT!'
        if description := request.form.get('description'):
            description = description[:10000]
        profile_image = False
        if profile_image := request.form.get('is_profile'):
            profile_image = True
            # unset previous profile image
            ENOFT.query.filter_by(owner_email=current_user.email, profile_image=True).update(
                {ENOFT.profile_image: False})
        new_enoft = ENOFT(
            image_path=file_name,
            certificate=certificate,
            owner_email=current_user.email,
            description=description,
            profile_image=profile_image)
        db.session.add(new_enoft)
        db.session.commit()
        self.img.close()
        flash('File uploaded')


def generate_unique_filename():
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

    return file_name


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
