from flask import Blueprint, session, g, render_template, redirect, url_for, flash, current_app
import pandas as pd
import os

import sqlite3
import click
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

from .. auth import login_required

bp = Blueprint('db', __name__, template_folder='pages', url_prefix='/db')

def get_db():
	db = sqlite3.connect(
		current_app.config['DATABASE'],
		detect_types=sqlite3.PARSE_DECLTYPES
		)
	db.row_factory =sqlite3.Row

	return db


def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()


def init_db():
	db = get_db()

	from ..auth import User
	from ..options import Options
	from ..account import Account
	from ..vendor import Vendor
	from ..cd import CD
	from ..ap import AP

	from ..x_cd import X_CD

	# This structure uses sqlite_data_model
	models = [User, Options, Account, Vendor,]
	for model in models:
		try:
			model(db=db).init_db
		except:
			pass
	
	# TODO: Codes below should be refactored to use sqlite_data_model
	CD(db=db).init_db
	AP(db=db).init_db

	X_CD(db=db).init_db

	defaults(db=db, company="wingain")


def defaults(db, company):
	#  Company options
	from ..options import Options

	company_options = pd.read_csv(os.path.join(current_app.instance_path, 'db_default', company, 'options.csv'))
	company_options.fillna("", inplace=True)

	for i, row in company_options.iterrows():
		key, value = row
		opt = Options(db=db)
		opt.keyword = key
		opt.value = value
		opt.save


	#  Users
	from ..auth import User
	users = pd.read_csv(os.path.join(current_app.instance_path, 'db_default', company, 'users.csv'))

	for i, user in users.iterrows():
		obj_user = User(
			db=db,
			username=user["username"],
			email=user["email"],
			password=user["password"],
			level=user["level"]
		)
		obj_user.save


	#  Accounts
	from ..account import Account
	accounts = pd.read_csv(os.path.join(current_app.instance_path, 'db_default', company, 'accounts.csv'))

	for i, row in accounts.iterrows():
		account = Account(
			db=db,
			account_number=row["account_number"],
			name=row["name"]
		)
		account.save


	#  Vendors
	from ..vendor import Vendor
	vendors = pd.read_csv(os.path.join(current_app.instance_path, 'db_default', company, 'vendors.csv'))
	vendors.fillna("", inplace=True)

	for i, row in vendors.iterrows():
		vendor = Vendor(
			db=db,
			name=row["name"],
			tin=row["tin"],
			address=row["address"]
		)
		vendor.save


@click.command('init-db')
@with_appcontext
def init_db_command():
	init_db()
	click.echo('Database has been initialized.')


def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)


@bp.route('/')
@login_required
def Home():
	return render_template('db/home.html')