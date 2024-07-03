from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import current_user
# from .models import Note
from . import logger
from .models import ENOFT


views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
async def home():
    return redirect(url_for('views.page', number=1))


@views.route('/page_<int:number>', methods=['GET'])
async def page(number):
    IMAGES_PER_PAGE = 5
    all_images = ENOFT.query.all()
    all_images.sort(key=lambda x: x.creation_date, reverse=True)
    if not all_images:
        logger.error("No images found in database.")
        all_images = []
    all_images = [(x.image_path, x.owner_email, x.description)
                  for x in all_images]
    # check limits
    if number < 1:
        flash('No such page', 'error')
        number = 1
    last_page = (len(all_images) // IMAGES_PER_PAGE) + 1
    if number > last_page:
        flash('No such page', 'error')
        number = last_page

    # get images
    images = all_images[(number - 1) *
                        IMAGES_PER_PAGE:number * IMAGES_PER_PAGE]
    logger.info("Home page accessed")
    return render_template(
        "home.html",
        user=current_user,
        images=images,
        page=number,
        max_pages=last_page,
        min_page=max(1, number - 5),
        max_page=min(last_page, number + 5)
    )
