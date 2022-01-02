from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g, send_file
from datetime import date, timedelta
import pandas as pd

from .. auth import login_required
from .. DB import get_db
from .. customer import Customer
from .. account import Account

from .dataclass import Sales, Create_File, get_sales

MAX_ROW = 10

bp = Blueprint('sales', __name__, template_folder="pages", url_prefix="/sales")


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
	sales = []

	for sale in Sales(db).range(date_from, date_to):
		id = sale['id']
		record_date = date(int(sale['record_date'][:4]), int(sale['record_date'][5:7]), int(sale['record_date'][-2:])).strftime("%d-%b-%Y")
		sales_num = sale['sales_num']
		customer_name = sale['customer_name']
		invoice_number = sale['invoice_number']

		sales.append(
			{
				'id': id,
				'record_date': record_date,
				'sales_num': sales_num,
				'customer_name': customer_name,
				'invoice_number': invoice_number
				}
			)

	return render_template('sales/home.html', sales=sales, date_from=date_from, date_to=date_to)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	db = get_db()
	customers = Customer(db=db).all()
	accounts = Account(db=db).all()
	sales = Sales(db=db)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('sales.Home'))
		else:
			sales.sales_num = request.form.get('sales_num')
			sales.record_date = str(request.form.get('record_date'))[:10]
			sales.customer_id = int(request.form.get('customer_id'))
			sales.invoice_number = request.form.get('invoice_number')
			sales.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				sales.add_entry(
					i=i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if sales.is_validated():
				sales.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('sales.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('sales.Edit', sales_id=sales.id))

	else:
		for i in range(0, MAX_ROW):
			sales.add_entry(i=i+1)

	form = sales

	return render_template('sales/add.html', form=form, customers=customers, accounts=accounts)


@bp.route('/edit/<int:sales_id>', methods=['POST', 'GET'])
@login_required
def Edit(sales_id):
	db = get_db()
	customers = Customer(db=db).all()
	accounts = Account(db=db).all()
	sale = Sales(db=db)
	sale.get(sales_id)

	if request.method == 'POST':
		if request.form.get('cmd_button') == "Back":
			return redirect(url_for('sales.Home'))
		elif request.form.get('cmd_button') == "Print":
			return redirect(url_for('sales.Print', sales_id=sales_id))
		else:
			sale.sales_num = request.form.get('sales_num')
			sale.record_date = str(request.form.get('record_date'))[:10]
			sale.customer_id = int(request.form.get('customer_id'))
			sale.invoice_number = request.form.get('invoice_number')
			sale.description = request.form.get('description')

			for i in range(0, MAX_ROW):
				i += 1
				sale.update_entry(
					i,
					account_id=int(request.form.get(f'{i}_account_id')),
					debit=request.form.get(f'{i}_debit'),
					credit=request.form.get(f'{i}_credit'),
					)

			if sale.is_validated():
				sale.save()
				if request.form.get('cmd_button') == "Save and New":
					return redirect(url_for('sales.Add'))
				elif request.form.get('cmd_button') == "Save":
					return redirect(url_for('sales.Edit', sales_id=sale.id))

	form = sale

	return render_template('sales/edit.html', form=form, customers=customers, accounts=accounts)


@bp.route('/delete/<int:sales_id>')
@login_required
def Delete(sales_id):
	db = get_db()
	sales = Sales(db=db)
	sales.get(sales_id)
	sales.delete()
	return redirect(url_for('sales.Home'))


@bp.route('/print/<int:sales_id>')
@login_required
def Print(sales_id):
	db = get_db()
	sales = Sales(db=db)
	sales.get(sales_id)
	_year = int(sales.record_date[:4])
	_month = int(sales.record_date[5:7])
	_day = int(sales.record_date[-2:])
	sales.record_date = date(_year, _month, _day).strftime("%B %d, %Y")
	for entry in sales.entry:
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

	return render_template('sales/print.html', sales=sales)


@bp.route('/download?<date_from>&<date_to>')
@login_required
def Download(date_from, date_to):
	f = Create_File(date_from=date_from, date_to=date_to)

	return send_file('{}'.format(f.filename), as_attachment=True, cache_timeout=0)


@bp.route('/view?<date_from>&<date_to>')
@login_required
def View(date_from, date_to):
	sales = get_sales(date_from, date_to)



	column_format = {}
	for key in sales.keys():
		if key not in ('DATE', 'SV No.', 'NAME', 'INVOICE No.', 'DESCRIPTION'):
			sales[key] = (
			    pd.to_numeric(sales[key],
			                  errors='coerce')
			      .fillna(0)
			    )

	sales = sales.append(sales.sum(numeric_only=True), ignore_index=True)
	sales = sales.fillna('')
	sales = sales.replace(0, '')

	return render_template('sales/view.html', sales=sales, date_from=date_from, date_to=date_to)


