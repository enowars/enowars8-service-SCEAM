from email.utils import parseaddr
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, send_from_directory, current_app
from .models import User
from flask_login import login_required, current_user
from .models import ENOFT
from .ENOFT_creator import ENOFT_creator
from .ENOFT_exporter import run as ENOFT_export


# user_profile = Blueprint('general', __name__)


# @user_profile.route('/styles.css', methods=['GET', 'POST'])
# @login_required
# async def stylesheet():
#     return render_template("styles.css")
