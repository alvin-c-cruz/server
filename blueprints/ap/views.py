from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, send_file
from datetime import date, timedelta
import pandas as pd

from .. auth import login_required
from .. DB import get_db
from .. vendor import Vendor
from .. account import Account

from .dataclass import AP, Create_File, get_ap

MAX_ROW = 10

bp = Blueprint('ap', __name__, template_folder="pages", url_prefix="/ap")


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
	aps = []


	for ap in AP(db).range(date_from, date_to):
		id = ap['id']
		record_date = date(int(ap['record_date'][:4]), int(ap['record_date'][5:7]), int(ap['record_date'][-2:])).strftime("%d-%b-%Y")
		ap_num = ap['ap_num']
		vendor_name = ap['vendor_name']
		invoice_number = ap['invoice_number']

		aps.append(
			{
				'id': id,
				'record_date': record_date,
				'ap_num': ap_num,
				'vendor_name': vendor_name,
				'invoice_number': invoice_number
				}
			)

	return render_template('ap/home.html', aps=aps, date_from=date_from, date_to=date_to)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	ap = AP(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('ap.Home'))
		else:
			ap.ap_num = request.form.get('ap_num')
			ap.record_date = str(request.form.get('record_date'))[:10]
			ap.vendor_id = int(request.form.get('vendor_id'))
			ap.invoice_number = request.form.get('invoice_number')
			ap.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				ap.add_entry(
					i=i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if ap.is_validated():
				ap.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('ap.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('ap.Edit', ap_id=ap.id))

	else:
		for i in range(0, MAX_ROW):
			ap.add_entry(i=i+1)

	form = ap

	return render_template('ap/add.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/edit/<int:ap_id>', methods=['POST', 'GET'])
@login_required
def Edit(ap_id):
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	ap = AP(db=db)
	ap.get(ap_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('ap.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('ap.Print', ap_id=ap_id))
		else:
			ap.ap_num = request.form.get('ap_num')
			ap.record_date = str(request.form.get('record_date'))[:10]
			ap.vendor_id = int(request.form.get('vendor_id'))
			ap.invoice_number = request.form.get('invoice_number')
			ap.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				ap.update_entry(
					i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if ap.is_validated():
				ap.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('ap.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('ap.Edit', ap_id=ap.id))

	form = ap

	return render_template('ap/edit.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/delete/<int:ap_id>')
@login_required
def Delete(ap_id):
	db = get_db()
	ap = AP(db=db)
	ap.get(ap_id)
	ap.delete()
	return redirect(url_for('ap.Home'))


@bp.route('/print/<int:ap_id>')
@login_required
def Print(ap_id):
	db = get_db()
	ap = AP(db=db)
	ap.get(ap_id)
	_year = int(ap.record_date[:4])
	_month = int(ap.record_date[5:7])
	_day = int(ap.record_date[-2:])
	ap.record_date = date(_year, _month, _day).strftime("%B %d, %Y")
	for entry in ap.entry:
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

	return render_template('ap/print.html', ap=ap)


@bp.route('/download?<date_from>&<date_to>')
@login_required
def Download(date_from, date_to):
	f = Create_File(date_from=date_from, date_to=date_to)

	return send_file('{}'.format(f.filename), as_attachment=True, cache_timeout=0)


@bp.route('/view?<date_from>&<date_to>')
@login_required
def View(date_from, date_to):
	aps = get_ap(date_from, date_to)



	column_format = {}
	for key in aps.keys():
		if key not in ('DATE', 'CD No.', 'NAME', 'INVOICE No.', 'DESCRIPTION'):
			aps[key] = (
			    pd.to_numeric(aps[key],
			                  errors='coerce')
			      .fillna(0)
			    )

	aps = aps.append(aps.sum(numeric_only=True), ignore_index=True)
	aps = aps.fillna('')
	aps = aps.replace(0, '')

	return render_template('ap/view.html', aps=aps, date_from=date_from, date_to=date_to)


