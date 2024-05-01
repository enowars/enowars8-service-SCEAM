from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, logger   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import email




user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile', methods=['GET', 'POST'])
def profile():
    return render_template("profile.html", user=current_user)



@user_profile.route('/create_enoft', methods=['GET', 'POST'])
def create_enoft():
    if request.method == 'GET':
        return render_template("create_enoft.html", user=current_user)
    
    
    
    return render_template("create_enoft.html", user=current_user)

