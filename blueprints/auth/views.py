from flask import Blueprint, session, g, render_template, redirect, url_for, flash, request, current_app
import functools
import click
from flask.cli import with_appcontext
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('auth', __name__, template_folder='pages', url_prefix='/auth')

@bp.route('/')
def Home():
	return "Users Home Page."

@bp.route('/login', methods=['POST', 'GET'])
def Login():
	if request.method == 'POST':
		username = request.form.get('username')
		password = request.form.get('password')
		error = None

		from .. DB import get_db
		from .dataclass import User
		db = get_db()
		user = User(db=db)
		user.find(username=username)

		if not user:
			error = "User is not registered"
		elif not check_password_hash(user.password, password):
			error = "Invalid password"
		
		if error is None:
			print('Hello World')
			session.clear()
			session['user_id'] = user.id
			return redirect(url_for('home_page.Home'))

		flash(error)

	return render_template('auth/login.html', program_title="Philgen Accounting")


@bp.route('/logout')
def Logout():
	session.clear()
	return redirect(url_for('auth.Login'))


@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')

	if user_id is None:
		g.user = None
	else:
		from .. DB import get_db
		from .dataclass import User
		user = User(get_db())
		user.get(user_id)
		g.user = user


def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.get('user') is None: return redirect(url_for('auth.Login'))
		return view(**kwargs)
	return wrapped_view



def add_user():
	username = input('Username: ')
	email = input('Email: ')
	password = input('Password: ')
	level = int(input('Level: '))
	
	from .. DB import get_db
	from .dataclass import User
	db = get_db()
	user = User(
		db=db,
		username=username,
		email=email,
		password=generate_password_hash(password),
		level=level
		)
	user.save()



@click.command('add-user')
@with_appcontext
def add_user_command():
	add_user()
	click.echo('Added new user...')


def user_app(app):
	from .. DB import close_db
	app.teardown_appcontext(close_db)
	app.cli.add_command(add_user_command)