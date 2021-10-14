from flask import Blueprint, session, g, render_template, redirect, url_for, flash

from .. DB import get_db
from .. auth  import login_required


bp = Blueprint('home_page', __name__, template_folder='pages')

@bp.route('/')
@login_required
def Home():
	db = get_db()
	return render_template('home_page/home.html')