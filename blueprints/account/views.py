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
				account_title=form['account_title']
				).save()
			flash(f"{form['account_number']}: {form['account_title']} has been saved.")

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
		account.account_title = form['account_title']

		if error:
			flash(error)
		else:
			account.save()
			flash(f"{form['account_number']}: {form['account_title']} has been saved.")

			return redirect(url_for('account.Home'))
		
	else:
		account.get(account_id)


	return render_template('account/edit.html', account=account, account_id=account_id)


def Validate(form, account_id=None):
	account_number = form.get('account_number')
	account_title =form.get('account_title')

	if not account_number: 
		return "Account Number is required."
	
	if not account_title: 
		return "Account Title is required."

	db = get_db()
	if account_id:
		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_number=? AND id!=?;", (account_number, account_id)).fetchone()[0]:
			return "Account Number is already in use."

		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_title=? AND id!=?;", (account_title, account_id)).fetchone()[0]:
			return "Account Title is already in use."
	else:
		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_number=?;", (account_number, )).fetchone()[0]:
			return "Account Number is already in use."

		if db.execute("SELECT COUNT(*) FROM tbl_account WHERE account_title=?;", (account_title, )).fetchone()[0]:
			return "Account Title is already in use."



@bp.route('/delete/<account_id>',methods=['POST', 'GET'])
@login_required
def Delete(account_id):
	db = get_db()
	account = Account(db=db)
	account.get(account_id)

	def is_related():
		if False:
			return True
		else:
			return False

	if not is_related():
		account.delete()
		flash(f"{account.account_title} has been deleted.")
	else:
		flash(f"{account.account_title} has related record(s) and cannot be deleted.")

	return redirect(url_for('account.Home'))
