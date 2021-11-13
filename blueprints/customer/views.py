from flask import Blueprint, session, g, flash, render_template, redirect, url_for, request
from .dataclass import Customer

from .. DB import get_db
from .. auth import login_required

bp = Blueprint('customer', __name__, template_folder='pages', url_prefix='/customer')



@bp.route('/')
@login_required
def Home():
	db = get_db()
	customers = Customer(db=db).all()
	return render_template('customer/home.html', customers=customers)


@bp.route('/add', methods=['POST', 'GET'])
@login_required
def Add():
	if request.method == 'POST':
		form = request.form

		error = Validate(form)

		if error:
			flash(error)
		else:
			db = get_db()
			customer = Customer(
				db=db, 
				name=form['name'], 
				tin=form['tin'],
				address=form['address']
				).save
			flash(f"{form['name']} has been saved.")

			if form['cmd_button'] == 'Save':
				return redirect(url_for('customer.Home'))
			else:
				return redirect(url_for('customer.Add'))

	else:
		form = ""

	return render_template('customer/add.html', form=form)


@bp.route('/edit/<customer_id>',methods=['POST', 'GET'])
@login_required
def Edit(customer_id):
	db = get_db()
	customer = Customer(db=db)
	
	if request.method == 'POST':
		form = request.form

		error = Validate(form, customer_id)

		customer.id = customer_id
		customer.name = form['name']
		customer.tin = form['tin']
		customer.address = form['address']

		if error:
			flash(error)
		else:
			customer.save
			flash(f"{form['name']} has been saved.")

			return redirect(url_for('customer.Home'))
		
	else:
		customer.get(id=customer_id)


	return render_template('customer/edit.html', customer=customer, customer_id=customer_id)


def Validate(form, customer_id=None):
	name = form.get('name')
	if not name: 
		return "Customer name is required."
	
	db = get_db()
	if customer_id:
		if db.execute("SELECT COUNT(*) FROM tbl_customer WHERE name=? AND id!=?;", (name, customer_id)).fetchone()[0]:
			return "Customer Name is already in use."

	else:
		if db.execute("SELECT COUNT(*) FROM tbl_customer WHERE name=?;", (name, )).fetchone()[0]:
			return "Customer Name is already in use."


@bp.route('/delete/<customer_id>',methods=['POST', 'GET'])
@login_required
def Delete(customer_id):
	db = get_db()
	customer = Customer(db=db)
	customer.get(id=customer_id)

	error = customer.delete

	if error:
		flash(f"{customer.name} has related record(s) and cannot be deleted.")
	else:
		flash(f"{customer.name} has been deleted.")

	return redirect(url_for('customer.Home'))
