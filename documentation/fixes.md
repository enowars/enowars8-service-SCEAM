# Email exploit

### replace the [uploads](/service/src/user_profile.py) function with the following

```python
@user_profile.route('/uploads/<path:path>', methods=['GET', 'POST'])
async def uploads(path):
    owner = ENOFT.query.filter_by(image_path=path).first()
    owner_email = owner.owner_email
    owner_name = User.query.filter_by(email=owner_email).first().name
    if session.get('name') is None:
        session_email = None
    else:
        session_email = parseaddr(session['name'])[1]
        session_name = parseaddr(session['name'])[0]
    owned = True if session_email == owner_email and session_name == owner_name else False
    force_lossy = User.query.filter_by(email=owner_email).first().quality
    if not owned or force_lossy:
        logger.info(
            f"User {session_email} accessed image {path} lossy version")
        return send_from_directory(
            current_app.config['LOSSY_IMAGE_UPLOADS'], path)
    else:
        logger.info(f"User {session_email} accessed image {path} full version")
        return send_from_directory(
            current_app.config['FULL_IMAGE_UPLOADS'], path)
```

# Crypto explot

### replace the [get_serialized](/service/src/ENOFT_exporter.py) function with the following

```python
def get_serialized(response):
    response['data'] = ''
    response['error'] = 'Something went wrong.'
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
    response['error'] = ''
    return response['data']

```
