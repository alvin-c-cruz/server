from flask import Blueprint, session, g, flash, render_template, redirect, url_for, request
from .dataclass import Account

from .. DB import get_db

bp = Blueprint('account', __name__, template_folder='pages', url_prefix='/account')



@bp.route('/')
def Home():
	db = get_db()
	accounts = Account(db=db).all()
	return render_template('account/home.html', accounts=accounts)


@bp.route('/add', methods=['POST', 'GET'])
def Add():
	if request.method == 'POST':
		pass
	else:
		form = ""

	return render_template('account/add.html', form=form)
