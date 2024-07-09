# Email exploit

### replace the [uploads](/service/src/user_profile.py) function with the following

```python
@user_profile.route('/uploads/<path:path>', methods=['GET', 'POST'])
async def uploads(path):
    owner_email = ENOFT.query.filter_by(image_path=path).first().owner_email
    owner_name = User.query.filter_by(email=owner_email).first().name
    if session.get('name') is None:
        session_email = None
    else:
        session_email = parseaddr(session['name'])[1]
        session_name = parseaddr(session['name'])[0]
    owned = True if session_email == owner_email and session_name == owner_name else False
    quality = User.query.filter_by(email=owner_email).first().quality
    if not owned or quality in [0, 2]:
        logger.info(
            f"User {session_email} accessed image {path} lossy version")
        get_lossy_image_path(path, quality)
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

# Bluring Exploit

### change the kernel or completely replace the blur:

```python
def get_lossy_image_path(path, quality):
    lossy_path = os.path.join(current_app.config['LOSSY_IMAGE_UPLOADS'], path)
    if not os.path.exists(lossy_path):
        full_path = os.path.join(
            current_app.config['FULL_IMAGE_UPLOADS'], path)
        img = Image.open(full_path)
        if quality in [0, 1]:
            new_size = (img.size[0] // DOWNSCALE_FACTOR,
                        img.size[1] // DOWNSCALE_FACTOR)
            small_image = img.resize(new_size, Resampling.NEAREST)
            small_image.save(lossy_path)
        elif quality == 2:
            blur_sigma = 6  # Standard deviation for Gaussian kernel
            kernel_size = 20  # Kernel size used for blurring
            kernel_1d = cv2.getGaussianKernel(kernel_size, blur_sigma)
            kernel = np.outer(kernel_1d, kernel_1d.transpose())
            img = np.array(img.convert('RGB'))
            blurred_img = np.zeros_like(img, dtype=np.float32)
            for i in range(3):
                blurred_img[:, :, i] = cv2.filter2D(img[:, :, i], -1, kernel)
            blurred_img_float = blurred_img.astype(float) / 255.0
            blurred_img_8bit = np.clip(
                blurred_img_float * 255, 0, 255).astype(np.uint8)
            cv2.imwrite(lossy_path, cv2.cvtColor(
                blurred_img_8bit, cv2.COLOR_RGB2BGR))
        elif quality == 3:
            img.save(lossy_path)

    return lossy_path
```
