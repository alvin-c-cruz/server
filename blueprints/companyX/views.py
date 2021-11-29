from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, send_file
from datetime import date, timedelta
import pandas as pd

from .. auth import login_required
from .. DB import get_db
from .. vendor import Vendor
from .. account import Account

from .dataclass import CompanyX, Create_File, get_cd

MAX_ROW = 10

bp = Blueprint('companyX', __name__, template_folder="pages", url_prefix="/companyX")


@bp.route('/', methods=['POST', 'GET'])
@login_required
def Home():
	if request.method == 'POST':
		date_from = request.form.get('date_from')
		date_to = request.form.get('date_to')
	else:
	    _date = date.today()
	    date_from = date(_date.year, _date.month, 1)
	    date_to = date(_date.year, _date.month + 1, 1) - timedelta(days=1)

	db = get_db()
	cds = []


	for cd in CompanyX(db).range(date_from, date_to):
		id = cd['id']
		record_date = date(int(cd['record_date'][:4]), int(cd['record_date'][5:7]), int(cd['record_date'][-2:])).strftime("%d-%b-%Y")
		cd_num = cd['cd_num']
		vendor_name = cd['vendor_name']
		check_number = cd['check_number']

		cds.append(
			{
				'id': id,
				'record_date': record_date,
				'cd_num': cd_num,
				'vendor_name': vendor_name, 
				'check_number': check_number
				}
			)

	return render_template('companyX/home.html', cds=cds, date_from=date_from, date_to=date_to)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	cd = CompanyX(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('companyX.Home'))
		else:
			cd.cd_num = request.form.get('cd_num')
			cd.record_date = str(request.form.get('record_date'))[:10]
			cd.vendor_id = int(request.form.get('vendor_id'))
			cd.check_notes = request.form.get('check_notes')
			cd.check_number = request.form.get('check_number')
			cd.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				cd.add_entry(
					i=i, 
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if cd.is_validated():
				cd.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('companyX.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('companyX.Edit', cd_id=cd.id))

	else:		
		for i in range(0, MAX_ROW):
			cd.add_entry(i=i+1)
	
	form = cd

	return render_template('companyX/add.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/edit/<int:cd_id>', methods=['POST', 'GET'])
@login_required
def Edit(cd_id):
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	cd = CompanyX(db=db)
	cd.get(cd_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('companyX.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('companyX.Print', cd_id=cd_id))
		else:
			cd.cd_num = request.form.get('cd_num')
			cd.record_date = str(request.form.get('record_date'))[:10]
			cd.vendor_id = int(request.form.get('vendor_id'))
			cd.check_notes = request.form.get('check_notes')
			cd.check_number = request.form.get('check_number')
			cd.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				cd.update_entry(
					i, 
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if cd.is_validated():
				cd.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('companyX.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('companyX.Edit', cd_id=cd.id))
	
	form = cd

	return render_template('companyX/edit.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/delete/<int:cd_id>')
@login_required
def Delete(cd_id):
	db = get_db()
	cd = CompanyX(db=db)
	cd.get(cd_id)
	cd.delete()
	return redirect(url_for('companyX.Home'))


@bp.route('/print/<int:cd_id>')
@login_required
def Print(cd_id):
	db = get_db()
	cd = CompanyX(db=db)
	cd.get(cd_id)
	_year = int(cd.record_date[:4])
	_month = int(cd.record_date[5:7])
	_day = int(cd.record_date[-2:])
	cd.record_date = date(_year, _month, _day).strftime("%B %d, %Y")
	for entry in cd.entry:
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

	return render_template('companyX/print.html', cd=cd)


@bp.route('/download?<date_from>&<date_to>')
@login_required
def Download(date_from, date_to):
	f = Create_File(date_from=date_from, date_to=date_to)
	
	return send_file('{}'.format(f.filename), as_attachment=True, cache_timeout=0)


@bp.route('/view?<date_from>&<date_to>')
@login_required
def View(date_from, date_to):
	cds = get_cd(date_from, date_to)



	column_format = {}
	for key in cds.keys():
		if key not in ('DATE', 'CD No.', 'NAME', 'CHECK No.', 'DESCRIPTION'):
			cds[key] = (
			    pd.to_numeric(cds[key],
			                  errors='coerce')
			      .fillna(0)
			    )			
	
	cds = cds.append(cds.sum(numeric_only=True), ignore_index=True)
	cds = cds.fillna('')
	cds = cds.replace(0, '')

	return render_template('companyX/view.html', cds=cds, date_from=date_from, date_to=date_to)


