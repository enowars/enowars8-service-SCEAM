from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_from_directory, current_app, send_file
from .models import User
from . import db, logger  # means from __init__.py import db
from flask_login import login_required, current_user
from .models import ENOFT
from .ENOFT_creator import ENOFT_creator
import io
from .ENOFT_exporter import run as ENOFT_export
import base64


user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile_<email>', methods=['GET', 'POST'])
@login_required
async def profile(email):

    session_email = parseaddr(session['name'])[1]
    owned = True if session_email == email else False

    if request.method == 'POST' and owned:
        ENOFT_creator()

    user = User.query.filter_by(email=email).first()
    enofts = ENOFT.query.filter_by(owner_email=user.email).all()
    file_names = [e.image_path for e in enofts]
    name = user.name + " <" + user.email + ">"

    return render_template("profile.html", user=current_user, images=file_names, owned=owned, name=name)


@user_profile.route('/uploads/<path:path>', methods=['GET', 'POST'])
@login_required
async def uploads(path):
    owner_email = ENOFT.query.filter_by(image_path=path).first().owner_email
    session_email = parseaddr(session['name'])[1]
    owned = True if session_email == owner_email else False
    force_lossy = User.query.filter_by(email=owner_email).first().never_full
    if not owned or force_lossy:
        return send_from_directory(current_app.config['LOSSY_IMAGE_UPLOADS'], path)
    else:
        return send_from_directory(current_app.config['FULL_IMAGE_UPLOADS'], path)


@user_profile.route('/export_<path:path>', methods=['GET', 'POST'])
@login_required
async def export(path):
    if request.method == 'GET':
        return render_template("export.html", user=current_user, img_path=path)

    if request.method == 'POST':
        res = ENOFT_export()
        if res['error'] != '':
            flash('Error during export: '+ res['error'], 'error')
            return redirect(url_for('user_profile.profile', email=current_user.email))

        session['img_path'] = path
        return render_template("show_serialization.html", user=current_user, certificate=res['data'])


@user_profile.route('/download_image', methods=['GET', 'POST'])
@login_required
async def download_image():
    path = session.pop('img_path', None)
    if path is None:
        return
    return send_from_directory(current_app.config['FULL_IMAGE_UPLOADS'], path)
