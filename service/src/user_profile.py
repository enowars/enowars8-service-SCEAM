from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_from_directory, current_app
from .models import User
from . import db, logger  # means from __init__.py import db
from flask_login import login_required, current_user
from .models import ENOFT
from .ENOFT_creator import ENOFT_creator
import os


user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile_<email>', methods=['GET', 'POST'])
@login_required
def profile(email):

    session_email = parseaddr(session['name'])[1]
    owned = True if session_email == email else False

    if request.method == 'POST' and owned:
        ENOFT_creator()

    user = User.query.filter_by(email=email).first()
    enofts = ENOFT.query.filter_by(user_id=user.id).all()
    file_names = [e.image_path for e in enofts]
    name = user.name + " <" + user.email + ">"

    return render_template("profile.html", user=current_user, images=file_names, owned=owned, name=name)


@user_profile.route('/uploads/<path:path>', methods=['GET', 'POST'])
@login_required
def uploads(path):
    owner_email = ENOFT.query.filter_by(image_path=path).first().email
    session_email = parseaddr(session['name'])[1]
    owned = True if session_email == owner_email else False
    if not owned:
        return send_from_directory(current_app.config['LOSSY_IMAGE_UPLOADS'], path)
    else:
        return send_from_directory(current_app.config['FULL_IMAGE_UPLOADS'], path)
