#
#	From the Python Flask tutorial github repository
#	https://github.com/pallets/flask/blob/3.0.0/examples/tutorial/flaskr
#

import sqlite3

import click
from flask import current_app
from flask import g
from werkzeug.security import generate_password_hash

def get_db():
	"""Connect to the application's configured database. The connection
	is unique for each request and will be reused if this is called
	again.
	"""
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row

	return g.db


def close_db(e=None):
	"""If this request connected to the database, close the
	connection.
	"""
	db = g.pop("db", None)

	if db is not None:
		db.close()


def init_db():
	"""Clear existing data and create new tables."""
	db = get_db()

	with current_app.open_resource("travelapp.sql") as f:
		db.executescript(f.read().decode("utf8"))


# seed database with some initial values for testing
def seed_db():
	q = "INSERT INTO user (username, password, first_name, last_name, email, bio) VALUES (?, ?, ?, ?, ?, ?)"
	cursor = None
	try:
		cursor = get_db().execute(q, ('test', generate_password_hash('test'), 'Test', 'User', 'test@example.com', 'Demo',))
		get_db().commit()
	except:
		pass
	q = "INSERT INTO itinerary (user_id, itinerary_name, country) VALUES (?, ?, ?)"
	last_row = cursor.lastrowid
	try:
		cursor = get_db().execute(q, (last_row, 'Aussie Trip #1', 'AU',))
		get_db().commit()
	except:
		pass
	q = "INSERT INTO places (itinerary_id, place, state) VALUES (?, ?, ?)"
	last_row = cursor.lastrowid
	try:
		get_db().execute(q, (last_row, 'Armidale', 'NSW',))
		get_db().commit()
		get_db().execute(q, (last_row, 'Tamworth', 'NSW',))
		get_db().commit()
		get_db().execute(q, (last_row, 'Gunnedah', 'NSW',))
		get_db().commit()
		get_db().execute(q, (last_row, 'Muswellbrook', 'NSW',))
		get_db().commit()
	except:
		pass


@click.command("init-db")
def init_db_command():
	"""Clear existing data and create new tables."""
	init_db()
	click.echo("Initialized the database.")


@click.command("seed-db")
def seed_db_command():
   """Seed the database with some initial data"""
   click.echo("Seeding database...")
   seed_db()
   click.echo("Done")
   

def init_app(app):
	"""Register database functions with the Flask app. This is called by
	the application factory.
	"""
	app.teardown_appcontext(close_db)
	app.cli.add_command(init_db_command)