from flask import Blueprint, session, g, flash, render_template, redirect, url_for
from ... packages import Voucher

bp = Blueprint('account', __name__, template_folder='pages', url_prefix='/account')



@bp.route('/')
def Home():
	accounts = []
	return render_template('account/home.html', accounts=accounts)