from flask import Blueprint, session, g, flash, render_template, redirect, url_for, request
from .dataclass import Account

from .. DB import get_db
from .. auth import login_required

bp = Blueprint('account', __name__, template_folder='pages', url_prefix='/account')



@bp.route('/')
@login_required
def Home():
	db = get_db()
	accounts = Account(db=db).all()
	return render_template('account/home.html', accounts=accounts)


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
			account = Account(
				db=db, 
				account_number=form['account_number'], 
				name=form['name']
				).save()
			flash(f"{form['account_number']}: {form['name']} has been saved.")

			if form['cmd_button'] == 'Save':
				return redirect(url_for('account.Home'))
			else:
				return redirect(url_for('account.Add'))

	else:
		form = ""

	return render_template('account/add.html', form=form)


@bp.route('/edit/<account_id>',methods=['POST', 'GET'])
@login_required
def Edit(account_id):
	db = get_db()
	account = Account(db=db)
	
	if request.method == 'POST':
		form = request.form

		error = Validate(form, account_id)

		account.id = account_id
		account.account_number = form['account_number']
		account.name = form['name']

		if error:
			flash(error)
		else:
			account.save()
			flash(f"{form['account_number']}: {form['name']} has been saved.")

			return redirect(url_for('account.Home'))
		
	else:
		account.get(account_id)


	return render_template('account/edit.html', account=account, account_id=account_id)


def Validate(form, account_id=None):
	account_number = form.get('account_number')
	name =form.get('name')

	if not account_number: 
		return "Account Number is required."
	
	if not name: 
		return "Account Title is required."

	db = get_db()
	if account_id:
		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_number=? AND id!=?;", (account_number, account_id)).fetchone()[0]:
			return "Account Number is already in use."

		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE name=? AND id!=?;", (name, account_id)).fetchone()[0]:
			return "Account Title is already in use."
	else:
		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_number=?;", (account_number, )).fetchone()[0]:
			return "Account Number is already in use."

		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE name=?;", (name, )).fetchone()[0]:
			return "Account Title is already in use."



@bp.route('/delete/<account_id>',methods=['POST', 'GET'])
@login_required
def Delete(account_id):
	db = get_db()
	account = Account(db=db)
	account.get(account_id)

	error = account.delete()

	if error:
		flash(f"{account.name} has related record(s) and cannot be deleted.")
	else:
		flash(f"{account.name} has been deleted.")

	return redirect(url_for('account.Home'))
