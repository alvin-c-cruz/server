from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, send_file
from datetime import date, timedelta
import pandas as pd

from .. auth import login_required
from .. DB import get_db
from .. customer import Customer
from .. account import Account

from .dataclass import CR, Create_File, get_cr

MAX_ROW = 10

bp = Blueprint('cr', __name__, template_folder="pages", url_prefix="/cr")


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
	crs = []

	for cr in CR(db).range(date_from, date_to):
		id = cr['id']
		record_date = date(int(cr['record_date'][:4]), int(cr['record_date'][5:7]), int(cr['record_date'][-2:])).strftime("%d-%b-%Y")
		cr_num = cr['cr_num']
		customer_name = cr['customer_name']
		or_number = cr['or_number']

		crs.append(
			{
				'id': id,
				'record_date': record_date,
				'cr_num': cr_num,
				'customer_name': customer_name,
				'or_number': or_number
				}
			)

	return render_template('cr/home.html', crs=crs, date_from=date_from, date_to=date_to)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	db = get_db()
	customers = Customer(db=db).all()
	accounts = Account(db=db).all()
	cr = CR(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('cr.Home'))
		else:
			cr.cr_num = request.form.get('cr_num')
			cr.record_date = str(request.form.get('record_date'))[:10]
			cr.customer_id = int(request.form.get('customer_id'))
			cr.or_number = request.form.get('or_number')
			cr.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				cr.add_entry(
					i=i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if cr.is_validated():
				cr.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('cr.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('cr.Edit', cr_id=cr.id))

	else:
		for i in range(0, MAX_ROW):
			cr.add_entry(i=i+1)

	form = cr

	return render_template('cr/add.html', form=form, customers=customers, accounts=accounts)


@bp.route('/edit/<int:cr_id>', methods=['POST', 'GET'])
@login_required
def Edit(cr_id):
	db = get_db()
	customers = Customer(db=db).all()
	accounts = Account(db=db).all()
	cr = CR(db=db)
	cr.get(cr_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('cr.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('cr.Print', cr_id=cr_id))
		else:
			cr.cr_num = request.form.get('cr_num')
			cr.record_date = str(request.form.get('record_date'))[:10]
			cr.customer_id = int(request.form.get('customer_id'))
			cr.or_number = request.form.get('or_number')
			cr.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				cr.update_entry(
					i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if cr.is_validated():
				cr.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('cr.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('cr.Edit', cr_id=cr.id))

	form = cr

	return render_template('cr/edit.html', form=form, customers=customers, accounts=accounts)


@bp.route('/delete/<int:cr_id>')
@login_required
def Delete(cr_id):
	db = get_db()
	cr = CR(db=db)
	cr.get(cr_id)
	cr.delete()
	return redirect(url_for('cr.Home'))


@bp.route('/print/<int:cr_id>')
@login_required
def Print(cr_id):
	db = get_db()
	cr = CR(db=db)
	cr.get(cr_id)
	_year = int(cr.record_date[:4])
	_month = int(cr.record_date[5:7])
	_day = int(cr.record_date[-2:])
	cr.record_date = date(_year, _month, _day).strftime("%B %d, %Y")
	for entry in cr.entry:
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

	return render_template('cr/print.html', cr=cr)


@bp.route('/download?<date_from>&<date_to>')
@login_required
def Download(date_from, date_to):
	f = Create_File(date_from=date_from, date_to=date_to)

	return send_file('{}'.format(f.filename), as_attachment=True, cache_timeout=0)


@bp.route('/view?<date_from>&<date_to>')
@login_required
def View(date_from, date_to):
	crs = get_cr(date_from, date_to)



	column_format = {}
	for key in crs.keys():
		if key not in ('DATE', 'SV No.', 'NAME', 'INVOICE No.', 'DESCRIPTION'):
			crs[key] = (
			    pd.to_numeric(crs[key],
			                  errors='coerce')
			      .fillna(0)
			    )

	crs = crs.append(crs.sum(numeric_only=True), ignore_index=True)
	crs = crs.fillna('')
	crs = crs.replace(0, '')

	return render_template('cr/view.html', crs=crs, date_from=date_from, date_to=date_to)


