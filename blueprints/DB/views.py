from flask import Blueprint, session, g, render_template, redirect, url_for, flash
from flask import current_app

import sqlite3
import click
from flask.cli import with_appcontext

from werkzeug.security import generate_password_hash

from .. auth import login_required

bp = Blueprint('db', __name__, template_folder='pages')

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
	from ..x_cd import XCD

	# This structure uses sqlite_data_model
	models = [Options]
	for model in models:
		try:
			model(db=db).delete_table
			model(db=db).create_table
		except:
			pass
	
	# TODO: Codes below should be refactored to use sqlite_data_model
	User(db=db).init_db
	Account(db=db).init_db
	Vendor(db=db).init_db
	CD(db=db).init_db
	XCD(db=db).init_db

	defaults(db=db, company="wingain")


def defaults(db, company):
	#  Company options
	from ..options import Options
	if company == "wingain":
		company_options = {
			'company_name': "WINGAIN CORPORATION",
			'cd_prepared': "MGV",
			'cd_checked': "ATVT",
			'cd_audited': "",
			'cd_approved': "ACV",
		}

	for key, value in company_options.items():
		opt = Options(db=db)
		opt.keyword = key
		opt.value = value
		opt.save


	#  Users
	from ..auth import User
	if company == "wingain":
		users = {

		}



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