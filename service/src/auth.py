from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, logger  # means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import email


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # handle first page request
    if request.method == 'GET':
        return render_template("login.html", user=current_user)

    # handle form submission
    email = request.form.get('email')
    private_key = request.form.get('private_key')
    name = request.form.get('name')

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
    encrypted = user.public_key.encrypt(example_message, padding.OAEP(
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
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        public_key, private_key = generate_keys()
        logger.info(
            f"Attempted Registration: {email} {name} {public_key} {private_key}")

        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already exists.', category='error')
            logger.error(f"Invalid")
        elif parseaddr(email)[1] == '':
            flash('Email is invalid', category='error')
        elif len(name) < 2:
            flash('Name must be greater than 1 character.', category='error')
        else:
            new_user = User(email=email, name=name, public_key=public_key)
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
def keyShowcase():
    private_key = session.pop('private_key', None)
    if private_key is None:
        return redirect(url_for('views.home'))

    # return private key to user
    return render_template("key_show.html", private_key=private_key, user=current_user)
