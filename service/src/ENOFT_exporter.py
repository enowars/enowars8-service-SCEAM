from flask import request
from . import logger
from .models import ENOFT, User
import base64
import cryptography
from cryptography.hazmat.primitives.serialization import BestAvailableEncryption
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from multiprocessing import Process, Manager
from .user_encryption_builder import UserInputParser
import time


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
        encryption_algorithm = get_encryption_algorithm(response)

        private_key = serialization.load_pem_private_key(
            response['private_key'], password=None, backend=default_backend())

        pkcs12_data = cryptography.hazmat.primitives.serialization.pkcs12.serialize_key_and_certificates(
            name=b'exported enoft',
            key=private_key,
            cert=certificate_decerialized,
            cas=[],
            encryption_algorithm=encryption_algorithm
        )
        response['data'] = base64.b64encode(pkcs12_data).decode('utf-8')
    except Exception as e:
        response['error'] = str(e)
        return None

    return response['data']


def get_encryption_algorithm(response):
    try:
        return UserInputParser(
            response['password'],
            response['encryption_algorithm']).run()
    except Exception as e:
        logger.error(e)
        return BestAvailableEncryption(str.encode(response['password']))


def run():
    if 'private_key' not in request.files:
        return {'error': 'Private Key invalid'}

    enoft = ENOFT.query.filter_by(image_path=request.form['img']).first()
    owner = User.query.filter_by(email=enoft.owner_email).first()
    if owner.vendor_lock:
        return {'error': 'Vendor Lock'}
    if not enoft:
        return {'error': 'Invalid Image'}
    res = {'error': 'serialization did not complete'}
    try:
        with Manager() as manager:
            res = manager.dict()
            try:
                res['enoft'] = enoft
                res['password'] = request.form['password']
                res['private_key'] = request.files['private_key'].read()
                res['encryption_algorithm'] = request.form['encryption_algorithm']
            except:
                res['error'] = "Invalid Request"
                return res

            t = Process(target=get_serialized, args=(res,))
            t.start()
            t.join()
            res = dict(res)
    except Exception as e:
        res['error'] = str(e)
    return res
