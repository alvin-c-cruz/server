from flask import Flask, session, g
import os
import secrets

from . import blueprints

def create_app(test_mode=False):
	app = Flask(__name__, instance_relative_config=True)
	app.config['SECRET_KEY'] = secrets.token_hex(16)
	app.config['TEST_MODE'] = test_mode

	if test_mode:
		app.config['DATABASE']=os.path.join('test', 'sqlite3.db')
		print(' * Test Mode =', test_mode)
	else:
		app.config['DATABASE']=os.path.join(app.instance_path, 'sqlite3.db')
		print(' * Test Mode = ', test_mode)


	# Ensure the instance and test folder exists
	required_folders = [
		app.instance_path,
		os.path.join(app.instance_path, 'downloads/'),
		'test',
	]
	for _dir in required_folders:
		try:
			os.makedirs(_dir)
		except OSError:
			pass

	views = [
		blueprints.options,
		blueprints.auth,
		blueprints.DB,

		blueprints.account,
		blueprints.vendor,
		blueprints.customer,

		blueprints.home_page,
		blueprints.sales,
		blueprints.cr,
		blueprints.cd,
		blueprints.ap,
		blueprints.gj,

		blueprints.x_home_page,
		blueprints.x_cd,
	]
	for view in views:
		app.register_blueprint(view.bp)

	blueprints.DB.init_app(app)
	blueprints.auth.user_app(app)

	return app