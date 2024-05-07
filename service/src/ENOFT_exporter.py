from flask import request, flash
from . import db, logger
from .models import ENOFT, User
import base64
import cryptography
from cryptography.hazmat.primitives.serialization import PrivateFormat, BestAvailableEncryption, pkcs12
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from multiprocessing import Process, Manager




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
    except Exception as e:
        print("DETECTED EXCEPTION:", e)
        response['error'] = str(e)
        return None

    pkcs12_data = base64.b64encode(pkcs12_data).decode('utf-8')
    return pkcs12_data

def get_encryption_algorithm(response):
    match response['encryption_algorithm']:
        case 'PBESv1SHA1And3KeyTripleDESCBC':
            encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().\
                    kdf_rounds(50000).\
                    key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And3KeyTripleDESCBC).\
                    build(str.encode(response['password']))
                    
        case 'PBESv1SHA1And40BitRC2CBC':
            encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().\
                    kdf_rounds(50000).\
                    key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And40BitRC2CBC).\
                    build(str.encode(response['password']))
                    
        case 'PBESv1SHA1And128BitRC4':
            encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().\
                    kdf_rounds(50000).\
                    key_cert_algorithm(pkcs12.PBES.PBESv1SHA1And128BitRC4).\
                    build(str.encode(response['password']))
                    
        case 'PBESv2SHA256AndAES256CBC':
            encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().\
                    kdf_rounds(50000).\
                    key_cert_algorithm(pkcs12.PBES.PBESv2SHA256AndAES256CBC).\
                    hmac_hash(hashes.SHA256()).build(str.encode(response['password']))
                    
        case 'SHA512':
            encryption_algorithm = PrivateFormat.PKCS12.encryption_builder().hmac_hash(
                    cryptography.hazmat.primitives.hashes.SHA512()).build(str.encode(response['password']))
        case _:
            encryption_algorithm = BestAvailableEncryption(str.encode(response['password']))
    return encryption_algorithm


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
            res['enoft'] = enoft
            res['password'] = request.form['password']
            res['private_key'] = request.files['private_key'].read()
            res['encryption_algorithm'] = request.form['encryption_algorithm']

            t = Process(target=get_serialized, args=(res,))
            t.start()
            t.join()
            res = dict(res)
    except Exception as e:
        res['error'] = str(e)

    return res
