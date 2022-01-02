from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, send_file
from datetime import date, timedelta
from openpyxl.descriptors.base import Descriptor
import pandas as pd

from .. auth import login_required
from .. DB import get_db
from .. vendor import Vendor
from .. account import Account

from .dataclass import GJ, CreateFile, get_gj

MAX_ROW = 10

bp = Blueprint('gj', __name__, template_folder="pages", url_prefix="/gj")


@bp.route('/', methods=['POST', 'GET'])
@login_required
def Home():
	if request.method == 'POST':
		date_from = request.form.get('date_from')
		date_to = request.form.get('date_to')
	else:
		_date = date.today()
		date_from = date(_date.year, _date.month, 1)
		date_to = date(
			_date.year if _date.month != 12 else _date.year+1,
			_date.month+1 if _date.month != 12 else 1,
			1) - timedelta(days=1)

	db = get_db()
	gjs = []


	for gj in GJ(db).range(date_from, date_to):
		id = gj['id']
		record_date = date(int(gj['record_date'][:4]), int(gj['record_date'][5:7]), int(gj['record_date'][-2:])).strftime("%d-%b-%Y")
		gj_num = gj['gj_num']
		description = gj['description']

		gjs.append(
			{
				'id': id,
				'record_date': record_date,
				'gj_num': gj_num,
				'description': description,
				}
			)

	return render_template('gj/home.html', gjs=gjs, date_from=date_from, date_to=date_to)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	db = get_db()
	accounts = Account(db=db).all()
	gj = GJ(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('gj.Home'))
		else:
			gj.gj_num = request.form.get('gj_num')
			gj.record_date = str(request.form.get('record_date'))[:10]
			gj.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				gj.add_entry(
					i=i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if gj.is_validated():
				gj.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('gj.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('gj.Edit', gj_id=gj.id))

	else:
		for i in range(0, MAX_ROW):
			gj.add_entry(i=i+1)

	form = gj

	return render_template('gj/add.html', form=form, accounts=accounts)


@bp.route('/edit/<int:gj_id>', methods=['POST', 'GET'])
@login_required
def Edit(gj_id):
	db = get_db()
	accounts = Account(db=db).all()
	gj = GJ(db=db)
	gj.get(gj_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('gj.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('gj.Print', gj_id=gj_id))
		else:
			gj.gj_num = request.form.get('gj_num')
			gj.record_date = str(request.form.get('record_date'))[:10]
			gj.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				gj.update_entry(
					i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if gj.is_validated():
				gj.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('gj.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('gj.Edit', gj_id=gj.id))

	form = gj

	return render_template('gj/edit.html', form=form, accounts=accounts)


@bp.route('/delete/<int:gj_id>')
@login_required
def Delete(gj_id):
	db = get_db()
	gj = GJ(db=db)
	gj.get(gj_id)
	gj.delete()
	return redirect(url_for('gj.Home'))


@bp.route('/print/<int:gj_id>')
@login_required
def Print(gj_id):
	db = get_db()
	gj = GJ(db=db)
	gj.get(gj_id)
	_year = int(gj.record_date[:4])
	_month = int(gj.record_date[5:7])
	_day = int(gj.record_date[-2:])
	gj.record_date = date(_year, _month, _day).strftime("%B %d, %Y")
	for entry in gj.entry:
		if entry.account_id != 0:
			entry.account_title = db.execute(
					'SELECT name FROM tbl_account WHERE id=?',
					(entry.account_id, )
				).fetchone()[0]

			if entry.debit != 0:
				entry.debit = '{:,.2f}'.format(entry.debit)

			if entry.credit != 0:
				entry.credit = '{:,.2f}'.format(entry.credit)
		else:
			entry.account_title = ""

	return render_template('gj/print.html', gj=gj)


@bp.route('/download?<date_from>&<date_to>')
@login_required
def Download(date_from, date_to):
	f = CreateFile(date_from=date_from, date_to=date_to)

	return send_file('{}'.format(f.filename), as_attachment=True, cache_timeout=0)


@bp.route('/view?<date_from>&<date_to>')
@login_required
def View(date_from, date_to):
	gjs = get_gj(date_from, date_to)

	column_format = {}
	for key in gjs.keys():
		if key not in ('DATE', 'CD No.', 'NAME', 'INVOICE No.', 'DESCRIPTION'):
			gjs[key] = (
			    pd.to_numeric(gjs[key],
			                  errors='coerce')
			      .fillna(0)
			    )

	gjs = gjs.append(gjs.sum(numeric_only=True), ignore_index=True)
	gjs = gjs.fillna('')
	gjs = gjs.replace(0, '')

	return render_template('gj/view.html', gjs=gjs, date_from=date_from, date_to=date_to)


