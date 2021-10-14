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
				vendor_name=form['vendor_name'], 
				tin=form['tin']
				).save()
			flash(f"{form['vendor_name']} has been saved.")

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
		vendor.vendor_name = form['vendor_name']
		vendor.tin = form['tin']

		if error:
			flash(error)
		else:
			vendor.save()
			flash(f"{form['vendor_name']} has been saved.")

			return redirect(url_for('vendor.Home'))
		
	else:
		vendor.get(vendor_id)


	return render_template('vendor/edit.html', vendor=vendor, vendor_id=vendor_id)


def Validate(form, vendor_id=None):
	vendor_name = form.get('vendor_name')

	if not vendor_name: 
		return "Vendor name is required."
	
	db = get_db()
	if vendor_id:
		if db.execute("SELECT COUNT(*) FROM tbl_vendor WHERE vendor_name=? AND id!=?;", (vendor_name, vendor_id)).fetchone()[0]:
			return "Vendor Name is already in use."

	else:
		if db.execute("SELECT COUNT(*) FROM tbl_vendor WHERE vendor_name=?;", (vendor_name, )).fetchone()[0]:
			return "Vendor Name is already in use."


@bp.route('/delete/<vendor_id>',methods=['POST', 'GET'])
@login_required
def Delete(vendor_id):
	db = get_db()
	vendor = Vendor(db=db)
	vendor.get(vendor_id)

	def is_related():
		if False:
			return True
		else:
			return False

	if not is_related():
		vendor.delete()
		flash(f"{vendor.vendor_name} has been deleted.")
	else:
		flash(f"{vendor.vendor_name} has related record(s) and cannot be deleted.")

	return redirect(url_for('vendor.Home'))
