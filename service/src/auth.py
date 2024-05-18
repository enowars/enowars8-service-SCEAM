from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_file, Response
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, logger  # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from io import BytesIO


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
async def login():
    # handle first page request
    if request.method == 'GET':
        return render_template("login.html", user=current_user)

    # handle form submission
    print(request.form)
    try:
        email = request.form.get('email')
        private_key = request.form.get('private_key')
        if 'file' not in request.files:
            flash("request.files: "+str(request.files), 'error')
            flash("request.form: "+str(request.form), 'error')

            print(request.files)
            flash('No file part', 'error')
            return login_error_handler("Private key not found.")
        private_key = request.files['file'].read()
        private_key = load_pem_private_key(private_key, password=None)

        name = request.form.get('name')
    except Exception as e:
        flash(e, category='error')
        return login_error_handler("Invalid form submission.")
    user = User.query.filter_by(email=email).first()
    if user == None:
        return login_error_handler(f"User with email {email} does not exist.")

    if user.name != name:
        return login_error_handler(f"User {user.name} with email {email} does not have name {name}.")

    if not valid_keys(private_key, user):
        return login_error_handler(f"Private key does not match public key for user with email {email}.")

    login_user(user, remember=True)
    set_session_name(user)
    flash('Logged in successfully!', category='success')
    return redirect(url_for('views.home'))


def valid_keys(private_key, user):
    example_message = b"example message to be encrypted"
    public_key = serialization.load_pem_public_key(user.public_key.encode())
    encrypted = public_key.encrypt(example_message, padding.OAEP(
        mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    decrypted = private_key.decrypt(encrypted, padding.OAEP(mgf=padding.MGF1(
        algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return decrypted == example_message


def login_error_handler(msg):
    errorString = "Credentials do not match."
    logger.info("LOGIN: "+msg)
    flash(errorString, category='error')
    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
async def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
async def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        never_full = request.form.get('never_full')
        vendor_lock = request.form.get('vendor_lock')
        never_full = True if never_full == 'on' else False
        vendor_lock = True if vendor_lock == 'on' else False
        public_key, private_key = generate_keys()
        logger.info(
            f"Attempted Registration: {email} {name} {public_key} {private_key} {never_full} {vendor_lock}")

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
            logger.error(f"Invalid")
        elif parseaddr(email)[1] == '':
            flash('Email is invalid', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        else:
            new_user = User(email=email, name=name,
                            public_key=public_key, never_full=never_full, vendor_lock=vendor_lock)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            session['private_key'] = private_key
            set_session_name(new_user)
            flash('Account created!', category='success')
            logger.info(f"Registration Success: {email}")
            return redirect(url_for('auth.keyShowcase'))

    return render_template("sign_up.html", user=current_user)


def generate_keys():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
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
    return render_template("key_show.html", private_key=private_key, user=current_user)


@auth.route('/download_key', methods=['POST', 'GET'])
async def download():
    private_key = session.pop('private_key', None)
    if private_key is None:
        return redirect(url_for('views.home'))

    return Response(
        private_key,
        mimetype="text/pem",
        headers={"Content-disposition":
                 "attachment; filename=private_key.pem"})
