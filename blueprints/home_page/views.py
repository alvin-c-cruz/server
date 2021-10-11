from flask import Blueprint, session, g, render_template, redirect, url_for, flash

from .. DB import get_db

bp = Blueprint('home_page', __name__, template_folder='pages')

@bp.route('/')
def Home():
	db = get_db()
	return render_template('home_page/home.html')