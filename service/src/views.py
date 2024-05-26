from flask import Blueprint, render_template, redirect, flash, url_for, session
from flask_login import login_required, current_user
# from .models import Note
from . import db, logger
from .models import ENOFT


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
async def home():
    return redirect(url_for('views.page', number=1))


@views.route('/page_<int:number>', methods=['GET'])
async def page(number):
    all_images = ENOFT.query.all()
    all_images.sort(key=lambda x: x.creation_date, reverse=True)
    if not all_images:
        logger.error("No images found in database.")
        all_images = []
    all_images = [x.image_path for x in all_images]
    # check limits
    if number < 1:
        flash('No such page', 'error')
        number = 1

    if number > len(all_images) // 10 + 1:
        flash('No such page', 'error')
        number = len(all_images) // 10 + 1

    # get images
    images = all_images[(number - 1) * 10:number * 10]

    return render_template(
        "home.html",
        user=current_user,
        images=images,
        page=number)
