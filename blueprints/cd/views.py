from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
from datetime import date

from .. auth import login_required
from .. DB import get_db
from .. vendor import Vendor
from .. account import Account

from .dataclass import CD

MAX_ROW = 15

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
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	cd = CD(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('cd.Home'))
		else:
			cd.cd_num = request.form.get('cd_num')
			cd.record_date = str(request.form.get('record_date'))[:10]
			cd.vendor_id = int(request.form.get('vendor_id'))
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
					return redirect(url_for('cd.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('cd.Edit', cd_id=cd.id))

	else:		
		for i in range(0, MAX_ROW):
			cd.add_entry(i=i+1)
	
	form = cd

	return render_template('cd/add.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/edit/<int:cd_id>', methods=['POST', 'GET'])
@login_required
def Edit(cd_id):
	db = get_db()
	vendors = Vendor(db=db).all()
	accounts = Account(db=db).all()
	cd = CD(db=db)
	cd.get(cd_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('cd.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('cd.Print', cd_id=cd_id))
		else:
			cd.cd_num = request.form.get('cd_num')
			cd.record_date = str(request.form.get('record_date'))[:10]
			cd.vendor_id = int(request.form.get('vendor_id'))
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
					return redirect(url_for('cd.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('cd.Edit', cd_id=cd.id))
	
	form = cd

	return render_template('cd/edit.html', form=form, vendors=vendors, accounts=accounts)


@bp.route('/delete/<int:cd_id>')
@login_required
def Delete(cd_id):
	db = get_db()
	cd = CD(db=db)
	cd.get(cd_id)
	cd.delete()
	return redirect(url_for('cd.Home'))


@bp.route('/print/<int:cd_id>')
@login_required
def Print(cd_id):
	db = get_db()
	cd = CD(db=db)
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

	return render_template('cd/print.html', cd=cd)

