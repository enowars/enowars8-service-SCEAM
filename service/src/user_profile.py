from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_from_directory, current_app
from .models import User
from flask_login import login_required, current_user
from .models import ENOFT
from .ENOFT_creator import ENOFT_creator
from .ENOFT_exporter import run as ENOFT_export
from . import logger
import os
from PIL import Image
from PIL.Image import Resampling
import numpy as np
import cv2

DOWNSCALE_FACTOR = 6
user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile_<email>', methods=['GET', 'POST'])
@login_required
async def profile(email):
    session_email = parseaddr(session['name'])[1]
    owned = True if session_email == email else False

    if request.method == 'POST' and owned:
        logger.info(f"User {session['name']} uploaded a new image")
        ENOFT_creator()

    user = User.query.filter_by(email=email).first()
    if user is None:
        flash(f"User with email {email} does not exist.", 'error')
        return redirect(url_for('views.home'))
    enofts = ENOFT.query.filter_by(owner_email=user.email).all()
    file_names = [e.image_path for e in enofts]
    name = user.name + " <" + user.email + ">"

    logger.info(f"User {name} profile accessed by {session['name']}")
    return render_template(
        "profile.html",
        user=current_user,
        images=file_names,
        owned=owned,
        name=name)

blur_sigma = 6  # Standard deviation for Gaussian kernel
kernel_size = 15  # Kernel size used for blurring
kernel_1d = cv2.getGaussianKernel(kernel_size, blur_sigma)
kernel = np.outer(kernel_1d, kernel_1d.transpose())


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
            img = np.array(img)
            blurred_img = np.zeros_like(img, dtype=np.float32)
            for i in range(3):
                blurred_img[:, :, i] = cv2.filter2D(img[:, :, i], -1, kernel)
            blurred_img_float = blurred_img.astype(float) / 255.0
            cv2.imwrite(lossy_path, blurred_img_float)
        elif quality == 3:
            img.save(lossy_path)

    return lossy_path


@user_profile.route('/uploads/<path:path>', methods=['GET', 'POST'])
async def uploads(path):
    owner_email = ENOFT.query.filter_by(image_path=path).first().owner_email
    if session.get('name') is None:
        session_email = None
    else:
        session_email = parseaddr(session['name'])[1]
    owned = True if session_email == owner_email else False
    quality = User.query.filter_by(email=owner_email).first().quality
    if not owned or quality == 0:
        logger.info(
            f"User {session_email} accessed image {path} lossy version")
        get_lossy_image_path(path, quality)
        return send_from_directory(
            current_app.config['LOSSY_IMAGE_UPLOADS'], path)
    else:
        logger.info(f"User {session_email} accessed image {path} full version")
        return send_from_directory(
            current_app.config['FULL_IMAGE_UPLOADS'], path)


@user_profile.route('/export_<path:path>', methods=['GET', 'POST'])
@login_required
async def export(path):
    if request.method == 'GET':
        logger.info(f"User {session['name']} exporting image {path}")
        return render_template("export.html", user=current_user, img_path=path)

    if request.method == 'POST':

        res = ENOFT_export()
        if res['error'] != '':
            flash('Error during export: ' + res['error'], 'error')
            logger.error(
                f"Error exporting image {path} by {session['name']}: {res['error']}")
            return redirect(
                url_for(
                    'user_profile.profile',
                    email=current_user.email))

        logger.info(
            f"User {session['name']} exported image {path} with {res['data']}")
        session['img_path'] = path
        return render_template(
            "show_serialization.html",
            user=current_user,
            certificate=res['data'])


@user_profile.route('/download_image', methods=['GET', 'POST'])
@login_required
async def download_image():
    path = session.pop('img_path', None)
    if path is None:
        return redirect(
            url_for(
                'user_profile.profile',
                email=current_user.email))
    logger.info(f"User {session['name']} downloading full res image {path}")
    return send_from_directory(current_app.config['FULL_IMAGE_UPLOADS'], path)
