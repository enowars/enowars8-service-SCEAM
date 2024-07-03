from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Response
from .models import User
from . import db, logger  # means from __init__.py import db
from datetime import timedelta
from flask_login import login_user, login_required, logout_user, current_user
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
async def login():
    # handle first page request
    if request.method == 'GET':
        return render_template("login.html", user=current_user)

    # handle form submission
    try:
        email = request.form.get('email')
        private_key = request.form.get('private_key')
        if 'file' not in request.files:
            flash('No file part', 'error')
            return login_error_handler(f"Private key not found in submition form: {email}")
        private_key = request.files['file'].read()
        private_key = load_pem_private_key(private_key, password=None)

        name = request.form.get('name')
        logger.info(f"Attempted Login: {email} {name} {private_key}")
    except Exception as e:
        flash(e, category='error')
        return login_error_handler("Invalid form submission.")
    user = User.query.filter_by(email=email).first()
    if user is None:
        return login_error_handler(f"User with email {email} does not exist.")

    if user.name != name:
        logger.error(
            f"LOGIN failed: name does not match {email} {name} {private_key} ")
        return login_error_handler(
            f"User {user.name} with email {email} does not have name {name}.")
    try:
        valid_keys(private_key, user)

    except Exception as e:
        return login_error_handler(
            f"Private key does not match public key for {email} {name} {private_key} {user.public_key} {e}")

    login_user(user, remember=True, duration=timedelta(minutes=10))
    set_session_name(user)
    flash('Logged in successfully!', category='success')
    return redirect(url_for('views.home'))


def valid_keys(private_key, user):
    example_message = b"example message to be encrypted"
    public_key = serialization.load_pem_public_key(user.public_key.encode())
    logger.info(f"created signature with {private_key}")
    signature = private_key.sign(
        example_message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    logger.info(
        f"verifying {private_key} with {signature} {example_message} {public_key}")

    public_key.verify(
        signature,
        example_message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )


def login_error_handler(msg):
    errorString = "Credentials do not match."
    logger.error("LOGIN failed: " + msg)
    flash(errorString, category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('name', None)
    session.pop('private_key', None)
    session.pop('img_path', None)
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
async def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        quality = request.form.get('quality')
        vendor_lock = request.form.get('vendor_lock')
        vendor_lock = True if vendor_lock == 'on' else False
        public_key, private_key = generate_keys()
        logger.info(
            f"Attempted Registration: {email} {name} {public_key} {private_key} {quality} {vendor_lock}")

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
        elif parseaddr(email)[1] == '':
            flash('Email is invalid', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        elif quality not in ["0", "1", "2", "3"]:
            flash('Unsupported Quality', category='error')
        else:
            new_user = User(
                email=email,
                name=name,
                public_key=public_key,
                quality=int(quality),
                vendor_lock=vendor_lock)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True, duration=timedelta(minutes=10))
            session['private_key'] = private_key
            set_session_name(new_user)
            flash('Account created!', category='success')
            logger.info(
                f"Registration Success: {email} {name} {public_key} {private_key} {quality} {vendor_lock}")
            return redirect(url_for('auth.keyShowcase'))
    return render_template("sign_up.html", user=current_user)


def generate_keys():
    key = rsa.generate_private_key(public_exponent=65537, key_size=512)
    public_key = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    private_key = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    return public_key, private_key


def set_session_name(user):
    encoded = f"{user.name} <{user.email}>"
    session['name'] = encoded


@auth.route('/key', methods=['GET', 'POST'])
async def keyShowcase():
    private_key = session.get('private_key', None)
    if private_key is None:
        return redirect(url_for('views.home'))
    return render_template(
        "key_show.html",
        private_key=private_key,
        user=current_user)


@auth.route('/download_key', methods=['POST', 'GET'])
async def download():
    private_key = session.pop('private_key', None)
    logger.info(f"Downloaded Key: {private_key}")
    if private_key is None:
        return redirect(url_for('views.home'))

    return Response(
        private_key,
        mimetype="text/pem",
        headers={"Content-disposition":
                 "attachment; filename=private_key.pem"})
