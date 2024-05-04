from flask import request, flash
from . import db, logger
from .models import ENOFT
import base64
import cryptography
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from multiprocessing import Process, Manager


def check_file_existence():
    if 'private_key' not in request.files:
        flash('Invalid Image', 'error')
        return False
    return True


def get_serialized(response):
    response['data'] = ''
    response['error'] = ''
    enoft = response['enoft']
    if not enoft:
        return None
    # catch exceptions and forward them
    try:
        certificate = enoft.certificate
        certificate_decoded = base64.b64decode(certificate)
        certificate_decerialized = cryptography.x509.load_pem_x509_certificate(
            certificate_decoded, default_backend())

        encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().hmac_hash(
            cryptography.hazmat.primitives.hashes.SHA256()).build(str.encode(response['password']))
        private_key = serialization.load_pem_private_key(
            response['private_key'], password=None, backend=default_backend())

    
        pkcs12_data = cryptography.hazmat.primitives.serialization.pkcs12.serialize_key_and_certificates(
            name=b'exported enoft',
            key=private_key,
            cert=certificate_decerialized,
            cas=[],
            encryption_algorithm=encryption_algorithm
        )
    except Exception as e:
        print("DETECTED EXCEPTION:", e)
        response['error'] = str(e)
        return None

    pkcs12_data = base64.b64encode(pkcs12_data).decode('utf-8')
    return pkcs12_data


def run():
    if 'private_key' not in request.files:
        return {'error': 'Private Key invalid'}


    enoft = ENOFT.query.filter_by(image_path=request.form['img']).first()
    if not enoft:
        return {'error': 'Invalid Image'}
    res = {'error': 'serialization did not complete'}
    with Manager() as manager:
        res = manager.dict()
        res['enoft'] = enoft
        res['password'] = request.form['password']
        res['private_key'] = request.files['private_key'].read()

        t = Process(target=get_serialized, args=(res,))
        t.start()
        t.join()
        res = dict(res)

    return res
