from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from . import db, logger  # means from __init__.py import db
from flask_login import login_required, current_user
from .models import ENOFT
from .ENOFT_creator import ENOFT_creator



user_profile = Blueprint('user_profile', __name__)


@user_profile.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        ENOFT_creator()

    return render_template("profile.html", user=current_user)
