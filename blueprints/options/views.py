from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
import functools

from .. auth import login_required
from .. DB import get_db

from .dataclass import Options

bp = Blueprint('options', __name__, template_folder="pages", url_prefix="/options")

@bp.route('/', methods=['POST', 'GET'])
def Home():
	if request.method == 'POST':
		form = request.form

		company_name = form['company_name']

		if not company_name:
			flash("Please type company name.")
		else:
			opt = Options(db=get_db())
			for keyword in (
					'company_name', 
					'sales_prepared', 'sales_checked', 'sales_audited', 'sales_approved',
					'cd_prepared', 'cd_checked', 'cd_audited', 'cd_approved',
					):
				opt.get(keyword=keyword)
				opt.value = form[keyword]
				opt.save
				session[keyword] = form[keyword]

			g.company_name = company_name

			g.sales_prepared = form['sales_prepared']
			g.sales_checked = form['sales_checked']
			g.sales_audited = form['sales_audited']
			g.sales_approved = form['sales_approved']

			g.cd_prepared = form['cd_prepared']
			g.cd_checked = form['cd_checked']
			g.cd_audited = form['cd_audited']
			g.cd_approved = form['cd_approved']

	else:
		form = {}

		opt = Options(db=get_db())
		opt.get(keyword='company_name')
		company_name = opt.value
		form['company_name'] = "" if company_name == "Company Name" else company_name

		for keyword in (
				'sales_prepared', 'sales_checked', 'sales_audited', 'sales_approved',
				'cd_prepared', 'cd_checked', 'cd_audited', 'cd_approved',
				):
			opt.get(keyword=keyword)
			value = opt.value
			form[keyword] = value

	return render_template('options/home.html', form=form)


