from flask import Blueprint, session, g, render_template, redirect, url_for, flash
import functools

bp = Blueprint('auth', __name__, template_folder='pages', url_prefix='/auth')

@bp.route('/')
def Home():
	return "Users Home Page."

@bp.route('/login')
def Login():
	return "Login Page."


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		# if g.get('user') is None: return redirect(url_for('auth.Login'))
		return view(**kwargs)
	return wrapped_view