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

		if not db.execute('SELECT username FROM tbl_user WHERE username=?;', (username, )).fetchone():
			error = "User is not registered"
		else:
			user.get(username=username)

			if not check_password_hash(user.password, password):
				error = "Invalid password"
		
		if error is None:
			session.clear()
			session['user_id'] = user.id
			return redirect(url_for('home_page.Home'))

		flash(error)

	return render_template('auth/login.html')


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
		user.get(id=user_id)
		g.user = user


@bp.before_app_request
def load_options():
	from .. DB import get_db
	from .. options import Options
	company_name = session.get('company_name')

	if current_app.config['TEST_MODE'] == True:
		session['user_id'] = 1

	if company_name is None:
		opt = Options(db=get_db())
		opt.get(keyword="company_name")
		company_name = opt.value
		g.company_name = company_name
		session['company_name'] = company_name
	else:
		g.company_name = company_name
	
	#  Sales Signatories
	if g.get('sales_prepared') is None:
		opt = Options(db=get_db())
		opt.get(keyword='sales_prepared')
		session['sales_prepared'] = opt.value
		g.sales_prepared = opt.value

	if g.get('sales_checked') is None:
		opt = Options(db=get_db())
		opt.get(keyword='sales_checked')
		session['sales_checked'] = opt.value
		g.sales_checked = opt.value

	if g.get('sales_audited') is None:
		opt = Options(db=get_db())
		opt.get(keyword='sales_audited')
		session['sales_audited'] = opt.value
		g.sales_audited = opt.value

	if g.get('sales_approved') is None:
		opt = Options(db=get_db())
		opt.get(keyword='sales_approved')
		session['sales_approved'] = opt.value
		g.sales_approved = opt.value


	#  CR signatories
	if g.get('cr_prepared') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cr_prepared')
		session['cr_prepared'] = opt.value
		g.cr_prepared = opt.value

	if g.get('cr_checked') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cr_checked')
		session['cr_checked'] = opt.value
		g.cr_checked = opt.value

	if g.get('cr_audited') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cr_audited')
		session['cr_audited'] = opt.value
		g.cr_audited = opt.value

	if g.get('cr_approved') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cr_approved')
		session['cr_approved'] = opt.value
		g.cr_approved = opt.value


	#  CD signatories
	if g.get('cd_prepared') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cd_prepared')
		session['cd_prepared'] = opt.value
		g.cd_prepared = opt.value

	if g.get('cd_checked') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cd_checked')
		session['cd_checked'] = opt.value
		g.cd_checked = opt.value

	if g.get('cd_audited') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cd_audited')
		session['cd_audited'] = opt.value
		g.cd_audited = opt.value

	if g.get('cd_approved') is None:
		opt = Options(db=get_db())
		opt.get(keyword='cd_approved')
		session['cd_approved'] = opt.value
		g.cd_approved = opt.value

	#  AP Signatories
	if g.get('ap_prepared') is None:
		opt = Options(db=get_db())
		opt.get(keyword='ap_prepared')
		session['ap_prepared'] = opt.value
		g.ap_prepared = opt.value

	if g.get('ap_checked') is None:
		opt = Options(db=get_db())
		opt.get(keyword='ap_checked')
		session['ap_checked'] = opt.value
		g.ap_checked = opt.value

	if g.get('ap_audited') is None:
		opt = Options(db=get_db())
		opt.get(keyword='ap_audited')
		session['ap_audited'] = opt.value
		g.ap_audited = opt.value

	if g.get('ap_approved') is None:
		opt = Options(db=get_db())
		opt.get(keyword='ap_approved')
		session['ap_approved'] = opt.value
		g.ap_approved = opt.value

#  GJ Signatories
	if g.get('gj_prepared') is None:
		opt = Options(db=get_db())
		opt.get(keyword='gj_prepared')
		session['gj_prepared'] = opt.value
		g.gj_prepared = opt.value

	if g.get('gj_checked') is None:
		opt = Options(db=get_db())
		opt.get(keyword='gj_checked')
		session['gj_checked'] = opt.value
		g.gj_checked = opt.value

	if g.get('gj_audited') is None:
		opt = Options(db=get_db())
		opt.get(keyword='gj_audited')
		session['gj_audited'] = opt.value
		g.gj_audited = opt.value

	if g.get('gj_approved') is None:
		opt = Options(db=get_db())
		opt.get(keyword='gj_approved')
		session['gj_approved'] = opt.value
		g.gj_approved = opt.value



	
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


