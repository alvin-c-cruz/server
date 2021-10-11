from flask import Blueprint, session, g, render_template, redirect, url_for, flash
from flask import current_app
import sqlite3

bp = Blueprint('db', __name__, template_folder='pages')

def get_db():
	db = sqlite3.connect(
		current_app.config['DATABASE'],
		detect_types=sqlite3.PARSE_DECLTYPES
		)
	db.row_factory =sqlite3.Row
	print(type(db))
	return db


@bp.route('/')
def Home():
	return render_template('db/home.html')