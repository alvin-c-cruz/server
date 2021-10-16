from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g

from .. auth import login_required
from .. DB import get_db

from .dataclass import CD

bp = Blueprint('cd', __name__, template_folder="pages", url_prefix="/cd")


@bp.route('/')
@login_required
def Home():
    db = get_db()
    cds = CD(db=db).all()
    return render_template('cd/home.html', cds=cds)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	form = {
			'entry': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
			}
	vendors = []
	return render_template('cd/add.html', form=form, vendors=vendors)


@bp.route('/edit')
@login_required
def Edit():
    return "Edit CD"


@bp.route('/delete')
@login_required
def Delete():
    return "Delete CD"

