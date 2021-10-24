from flask import Blueprint, session, g, render_template, redirect, url_for, flash
from flask import current_app

import sqlite3
import click
from flask.cli import with_appcontext

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
	from ..account import Account
	from ..vendor import Vendor
	from ..cd import CD

	User(db=db).init_db
	Account(db=db).init_db
	Vendor(db=db).init_db
	CD(db=db).init_db


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