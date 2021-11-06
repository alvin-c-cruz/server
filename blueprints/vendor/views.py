from flask import Blueprint, session, g, flash, render_template, redirect, url_for, request
from .dataclass import Vendor

from .. DB import get_db
from .. auth import login_required

bp = Blueprint('vendor', __name__, template_folder='pages', url_prefix='/vendor')



@bp.route('/')
@login_required
def Home():
	db = get_db()
	vendors = Vendor(db=db).all()
	return render_template('vendor/home.html', vendors=vendors)


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
			vendor = Vendor(
				db=db, 
				name=form['name'], 
				tin=form['tin'],
				address=form['address']
				).save()
			flash(f"{form['name']} has been saved.")

			if form['cmd_button'] == 'Save':
				return redirect(url_for('vendor.Home'))
			else:
				return redirect(url_for('vendor.Add'))

	else:
		form = ""

	return render_template('vendor/add.html', form=form)


@bp.route('/edit/<vendor_id>',methods=['POST', 'GET'])
@login_required
def Edit(vendor_id):
	db = get_db()
	vendor = Vendor(db=db)
	
	if request.method == 'POST':
		form = request.form

		error = Validate(form, vendor_id)

		vendor.id = vendor_id
		vendor.name = form['name']
		vendor.tin = form['tin']
		vendor.address = form['address']

		if error:
			flash(error)
		else:
			vendor.save()
			flash(f"{form['name']} has been saved.")

			return redirect(url_for('vendor.Home'))
		
	else:
		vendor.get(vendor_id)


	return render_template('vendor/edit.html', vendor=vendor, vendor_id=vendor_id)


def Validate(form, vendor_id=None):
	name = form.get('name')

	if not name: 
		return "Vendor name is required."
	
	db = get_db()
	if vendor_id:
		if db.execute("SELECT COUNT(*) FROM tbl_vendor WHERE name=? AND id!=?;", (name, vendor_id)).fetchone()[0]:
			return "Vendor Name is already in use."

	else:
		if db.execute("SELECT COUNT(*) FROM tbl_vendor WHERE name=?;", (name, )).fetchone()[0]:
			return "Vendor Name is already in use."


@bp.route('/delete/<vendor_id>',methods=['POST', 'GET'])
@login_required
def Delete(vendor_id):
	db = get_db()
	vendor = Vendor(db=db)
	vendor.get(vendor_id)

	error = vendor.delete()

	if error:
		flash(f"{vendor.name} has related record(s) and cannot be deleted.")
	else:
		flash(f"{vendor.name} has been deleted.")

	return redirect(url_for('vendor.Home'))
