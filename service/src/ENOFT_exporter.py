from flask import request, current_app, flash
from . import db, logger
from .models import ENOFT
import base64
import cryptography
import zipfile
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


class ENOFT_export:
    
    def __init__(self):
        print("started ENOFT_export init")
        self.valid = True
        self.img_path = request.form['img']
        self.password = request.form['password']
        self.check_file_existence()
        self.validate_image()
        self.get_serialized()


        
    def shortcuircuit(foo):
        def check(self):
            if not self.valid:
                return
            foo(self)
        return check
    
    @shortcuircuit
    def check_file_existence(self):
        if 'private_key' not in request.files:
            print("No file part")
            flash('No file part', 'error')
            self.valid = False
    
    def validate_image(self):
        self.enoft = ENOFT.query.filter_by(image_path=self.img_path).first()
        if not self.enoft:
            self.valid = False
            return
    
        
    @shortcuircuit
    def get_serialized(self):
        certificate = self.enoft.certificate
        certificate_decoded = base64.b64decode(certificate)
        certificate_decerialized = cryptography.x509.load_pem_x509_certificate(certificate_decoded, default_backend())
        

        encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().hmac_hash(
            cryptography.hazmat.primitives.hashes.SHA256()).build(str.encode(self.password))
        self.private_key = request.files['private_key']
        self.private_key = serialization.load_pem_private_key(self.private_key.read(), password=None, backend=default_backend())

        
        
        pkcs12_data = cryptography.hazmat.primitives.serialization.pkcs12.serialize_key_and_certificates(
            name=b'exported enoft',
            key=self.private_key,
            cert=certificate_decerialized,
            cas=[],
            encryption_algorithm=encryption_algorithm
        )
        

        
        # pkcs12_data = base64.b64encode(pkcs12_data).decode('utf-8')
        print("returning pkcs12_data")
        pkcs12_data = base64.b64encode(pkcs12_data).decode('utf-8')
        self.export = pkcs12_data
        return pkcs12_data
    
