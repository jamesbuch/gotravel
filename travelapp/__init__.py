#
#	Go Travel! COS60016 Assignment 2
#	James Buchanan
#	jamesbuch1337@gmail.com
#

import os
import secrets
import requests
import json

# For debugging
from pprint import pprint

from datetime import datetime, date, time
from flask import Flask, redirect, flash, render_template, request, url_for, session
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Import libraries for chat function.
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

# register the database commands
from travelapp import db

#
#	From the Python Flask tutorial github repository
#	https://github.com/pallets/flask/blob/3.0.0/examples/tutorial/flaskr
# 	create_app
# 	Modified for travelapp
#
def create_app(test_config=None):
	
	app = Flask(__name__, instance_relative_config=True)
	
	app.config.from_mapping(
		SECRET_KEY=secrets.token_hex(),
		DATABASE=os.path.join(app.instance_path, "travelapp.sqlite"),
	)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	db.init_app(app)
 
	@app.route('/weather', methods=['POST'])
	def weather():
		load_dotenv()
		data = request.json
		# Return JSON data, this is an internal API call
		# Calls OpenWeatherMap's API to retrieve the result
		# https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&exclude={part}&appid={API key}
		url = 'https://api.openweathermap.org/data/2.5/forecast?lat=' + data['lat'] + '&lon=' + data['lon'] + '&appid=' + os.environ['OPENWEATHER_API_KEY'] + '&units=metric'
		r = requests.get(url)
		return r.json()

	
	# If the request method is GET, return the template for input.
	# If the method is POST, the user has submitted the form for a response
	@app.route('/chat', methods=['GET', 'POST'])
	def chat():
    
		load_dotenv()
  
		if request.method == 'GET':
			return render_template('chat.html', chat_response=False, userid=session.get('user_id'), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))
  
		# Create a new ChatBot instance
		bot = ChatBot(
			'Weatherbot',
			logic_adapters=[
				'chatterbot.logic.BestMatch',
				{
						'import_path': 'weather_adapter.WeatherLogicAdapter'
				}
			]
		)

		# Example chats, it's sometimes difficult to extract a location to provide
		# a useful answer; this is the job of the WeatherLogicAdapter class
		weather_talk = [
			"Weather please",
			"Sure. Please tell me the city name and country for a weather report, e.g. London, UK",
			"Get forecast",
			"Please input the location for a forecast",
			"What's the weather forecast",
			"Please type the city name for a forecast",
			"What's the weather like",
			"I can give a weather report, please type the city name",
			"Temperatures",
			"It sounds like you want a weather forecast, please enter the city name",
			"Will there be rain",
			"Please enter the city and I will check",
			"Is it going to be sunny",
			"Please enter the city and I will check",
			"Can you tell me the weather",
			"Yes, I can! Please type the city name",
			"Forecast",
			"Please enter a location for a forecast",
			"weather",
			"I am a weather bot, please enter a location for a weather report",
			"Is it going to rain",
			"I can tell you, please enter a city name",
			"Get forecast",
			"I can get you a forecast, please enter a location",
			"What is the forecast",
			"Please enter a city name and I can find out",
			"Weather forecast for 7 days",
			"Sure, please enter a location",
			"Forecast for 3 days",
			"No problem, please enter a city name",
			"Weather report",
			"No problem, please enter a city",
			"Weather report for 7 days",
			"Please enter a location for a weather report",
			"Tell me the forecast",
			"Absolutely, please enter a location",
			"Tell me the weather",
			"Sure, please enter a location"
		]

		list_trainer = ListTrainer(bot)

		for item in weather_talk:
			list_trainer.train(item)
  
		bot_input = request.form['question']
		bot_response = bot.get_response(bot_input)

		rc = bot_response.text.replace("'", '"')
		res = None
  
		if rc.startswith('[{'):
			res = json.loads(rc)
			return render_template('chat.html', chat_response=True, singleLine=False, response=res, userid=session.get('user_id'), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))
		
		res = str(rc)
		return render_template('chat.html', chat_response=True, singleLine=True, response=res, userid=session.get('user_id'), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))


	@app.route('/')
	def index():
		posts = query_db('SELECT * FROM posts')
		itinerary_details = get_all_itineraries()
		return render_template('index.html', posts=posts, itineraries=itinerary_details, userid=session.get('user_id'), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))


	@app.route('/itinerary', methods=['GET', 'POST'])
	def itinerary():
		if request.method == 'POST':
			# Request method is POST, insert itinerary data
			q = "INSERT INTO itinerary (user_id, itinerary_name, country) VALUES (?, ?, ?)"
			cursor = None
			try:
				cursor = db.get_db().execute(q, (request.form['userid'], request.form['name'], request.form['country'],))
				db.get_db().commit()
			except db.get_db().DatabaseError:
				flash('Failed to insert itinerary data')
				return render_template('itinerary.html', userid=str(session.get('user_id')), name=session.get('name'), email=session.get('email'), logged_in=session.get('logged_in'))
			except db.get_db().DataError:
				flash('Failed to insert itinerary data')
				return render_template('itinerary.html', userid=str(session.get('user_id')), name=session.get('name'), email=session.get('email'), logged_in=session.get('logged_in'))
			except db.get_db().IntegrityError:
				flash('Failed to insert itinerary data')
				return render_template('itinerary.html', userid=str(session.get('user_id')), name=session.get('name'), email=session.get('email'), logged_in=session.get('logged_in'))
			# Get the places in itinerary and enter into database
			places = request.form['places'].split('\n')
			for place in places:
				p = place.split(',')
				has_state = len(p) > 1
				print(f'Place {place}')
				for pl in p:
					print(f'Place part: {pl}')
				if not has_state:
					q = "INSERT INTO places (itinerary_id, place) VALUES (?, ?)"
					try:
						db.get_db().execute(q, (cursor.lastrowid, place.strip(),))
						db.get_db().commit()
					except db.get_db().DatabaseError:
						flash('Failed to insert itinerary data')
				else:
					q = "INSERT INTO places (itinerary_id, place, state) VALUES (?, ?, ?)"
					try:
						db.get_db().execute(q, (cursor.lastrowid, p[0].strip(), p[1].strip(),))
						db.get_db().commit()
					except db.get_db().DatabaseError:
						flash('Failed to insert itinerary data')
      
		if session.get('user_id') is not None:
			itineraries = get_my_itineraries(session.get('user_id'))
		else:
			itineraries = get_all_itineraries()
		return render_template('itinerary.html', itineraries=itineraries, userid=str(session.get('user_id')), name=session.get('name'), email=session.get('email'), logged_in=session.get('logged_in'))


	@app.route('/register', methods=['GET', 'POST'])
	def register():
    
		if request.method == 'POST':
			
			errors = False
			username = request.form.get('username')
			password = request.form.get('password')
			email = request.form.get('email')
			fname = request.form.get('fname')
			lname = request.form.get('lname')
			bio = request.form.get('bio')

			if not email:
				flash("email is required")
				errors = True
			if not username:
				flash("Username is required")
				errors = True
			if not password:
				flash("Password is required")
				errors = True
			if not fname:
				flash("First name is required")
				errors = True
			if not lname:
				flash("Last name is required")
				errors = True

			if not errors:
				if not bio:
					bio = ""
				regiser_user(email, username, password, fname, lname, bio)
				posts = query_db('SELECT * FROM posts WHERE author_id = ?', (session.get('user_id'),))
				itineraries = query_db('SELECT * FROM itinerary WHERE user_id = ?', (session.get('user_id'),))
				itinerary_details = {}
				for i in itineraries:
					place = query_db('SELECT * FROM places WHERE itinerary_id = ?', (i['id']))
					places = []
					for p in place:
						places.append(p)
					itinerary_details[i['itinerary_name']] = places
				return render_template('index.html', posts=posts, itineraries=itineraries, places=itinerary_details, userid=session.get('user_id'), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))

		return render_template('register.html')

	
	@app.route('/login', methods=['GET', 'POST'])
	def login():
		if request.method == 'POST':
			
			errors = False
			email = request.form.get('email')
			password = request.form.get('password')
			
			if not email:
				flash("email is required")
				errors = True
			if not password:
				flash("Password is required")
				errors = True
			if not errors:
				ok = login_user(email, password)
				if not ok:
					return render_template('login.html')

				posts = query_db('SELECT * FROM posts WHERE author_id = ?', (session.get('user_id'),))
				itineraries = get_my_itineraries(session.get('user_id'))
				return render_template('index.html', posts=posts, itineraries=itineraries, userid=str(session.get('user_id')), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))
 
		return render_template('login.html')


	@app.route('/forecast/itinerary', methods=['POST'])
	def forecast():
		load_dotenv()
		itinerary_name = request.form['itinerary']
		it = query_db('SELECT * FROM itinerary WHERE itinerary_name = ? LIMIT 1', (itinerary_name,))
		id = it[0]['id']
		name = it[0]['itinerary_name']
		country = it[0]['country']
		places = query_db('SELECT * FROM places WHERE itinerary_id = ?', (str(id)))
		it_places = []
		for p in places:
			pl = p['place']
			if p['state'] is not None:
				pl = pl + ', ' + p['state']
			pl = pl + ', ' + country
			it_places.append(pl)
		forecast_data = []
		for p in it_places:
			pl = p.split(', ')
			# This is a hack to get around openweathermap not knowing about some places; instead
			# if lat, lon coordinates are in the database, use them instead
			url = ""
			city_coords = find_lat_lon(request.form['city'])
			if len(city_coords) > 0:
				url = 'https://api.openweathermap.org/data/2.5/forecast?lat=' + city_coords[0] + '&lon=' + city_coords[1] + '&appid=' + os.environ['OPENWEATHER_API_KEY'] + '&units=metric'
			else:
				url = 'https://api.openweathermap.org/data/2.5/forecast?q=' + p + '&appid=' + os.environ['OPENWEATHER_API_KEY'] + '&units=metric'
			r = requests.get(url)
			json_data = r.json()
			if int(json_data['cod']) != 200:
				flash('Openweathermap Error Message: ' + json_data['message'])
				break
			weather = []
			for item in json_data['list']:
				dt = datetime.fromtimestamp(item['dt'])
				dts = dt.strftime('%I:%M %p')
				if dts.find('8:00 AM') > -1 or dts.find('2:00 PM') > -1 or dts.find('8:00 PM') > -1:
					w = { 'datetime': dts, 'day': dt.strftime('%A'), 'temp': item['main']['temp'], 'feels_like': item['main']['feels_like'], 'min': item['main']['temp_min'], 'max': item['main']['temp_max'], 'main': item['weather'][0]['main'], 'desc': item['weather'][0]['description'].capitalize(), 'icon': 'http://openweathermap.org/img/wn/' + item['weather'][0]['icon'] + '@2x.png' }
					weather.append(w)
			result = { 'city': pl[0], 'weather': weather }
			forecast_data.append(result)
		return render_template('forecast.html', weather=forecast_data, userid=str(session.get('user_id')), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))


	@app.route('/forecast/place', methods=['POST'])
	def forecast_city():
		load_dotenv()
		weather = []
		# This is a hack to get around openweathermap not knowing about some places; instead
		# if lat, lon coordinates are in the database, use them instead
		url = ""
		city_coords = find_lat_lon(request.form['city'])
		if len(city_coords) > 0:
			url = 'https://api.openweathermap.org/data/2.5/forecast?lat=' + city_coords[0] + '&lon=' + city_coords[1] + '&appid=' + os.environ['OPENWEATHER_API_KEY'] + '&units=metric'
		else:
			url = 'https://api.openweathermap.org/data/2.5/forecast?q=' + request.form['city'] + '&appid=' + os.environ['OPENWEATHER_API_KEY'] + '&units=metric'
		r = requests.get(url)
		json_data = r.json()
		print(request.form['city'])
		pprint(json_data)
		if int(json_data['cod']) != 200:
			flash('Openweathermap Error Message: ' + json_data['message'])
			return render_template('forecast_city.html', weather=weather, userid=str(session.get('user_id')), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))
		for item in json_data['list']:
			dt = datetime.fromtimestamp(item['dt'])
			dts = dt.strftime('%I:%M %p')
			if dts.find('8:00 AM') > -1 or dts.find('2:00 PM') > -1 or dts.find('8:00 PM') > -1:
				w = { 'city': request.form['city'], 'datetime': dts, 'day': dt.strftime('%A'), 'temp': item['main']['temp'], 'feels_like': item['main']['feels_like'], 'min': item['main']['temp_min'], 'max': item['main']['temp_max'], 'main': item['weather'][0]['main'], 'desc': item['weather'][0]['description'].capitalize(), 'icon': 'http://openweathermap.org/img/wn/' + item['weather'][0]['icon'] + '@2x.png' }
				weather.append(w)
		return render_template('forecast_city.html', weather=weather, userid=str(session.get('user_id')), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))


	@app.route('/about')
	def about():
		return render_template('about.html')


	@app.route('/logout')
	def logout():
		session.pop('email', None)
		session.pop('user_id', None)
		session.pop('name', None)
		session['logged_in'] = False
		return render_template('index.html', posts=list(), itineraries=list(), userid=str(session.get('user_id')), logged_in=session.get('logged_in'), name=session.get('name'), email=session.get('email'))

	return app


def query_db(query, args=(), one=False):
	cur = db.get_db().execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv
 

def login_user(email, password):
	user = query_db("SELECT * FROM user WHERE email = ?", (email,), True)
	if not user:
		session['logged_in'] = False
		flash("No user with that email address")
		return False
	if not check_password_hash(user['password'], password):
		session['logged_in'] = False
		flash("Incorrect password")
		return False
	session['logged_in'] = True
	session['user_id'] = user['id']
	session['name'] = user['first_name']
	session['email'] = user['email']
	return True


def regiser_user(email, username, password, first_name, last_name, bio=""):
	
	q = "INSERT INTO user (username, password, first_name, last_name, email, bio) VALUES (?, ?, ?, ?, ?, ?)"
	
	try:
		db.get_db().execute(q, (username, generate_password_hash(password), first_name, last_name, email, bio,))
		db.get_db().commit()
	except db.get_db().IntegrityError:
		flash('User with that email already exists')
		return render_template('register.html')
	
	return render_template('login.html')


def get_all_itineraries():
	itineraries = query_db('SELECT * FROM itinerary')
	itinerary_details = []
	for i in itineraries:
		place = query_db('SELECT * FROM places WHERE itinerary_id = ?', (str(i['id'])))
		places = []
		for p in place:
			pl = p['place']
			if p['state'] is not None:
				pl = pl + ', ' + p['state']
			places.append(pl)
		details = { 'name': i['itinerary_name'], 'country': i['country'], 'places': places }
		itinerary_details.append(details)
	return itinerary_details


def get_my_itineraries(user_id):
	itineraries = query_db('SELECT * FROM itinerary WHERE user_id = ?', str(user_id))
	itinerary_details = []
	for i in itineraries:
		place = query_db('SELECT * FROM places WHERE itinerary_id = ?', (str(i['id'])))
		places = []
		for p in place:
			pl = p['place']
			if p['state'] is not None:
				pl = pl + ', ' + p['state']
			places.append(pl)
		details = { 'name': i['itinerary_name'], 'country': i['country'], 'places': places }
		itinerary_details.append(details)
	return itinerary_details


def find_lat_lon(city):
	# city names can come in with ', country' on the end, it still works with just a city name
   p = city.split(',')
   q = query_db('SELECT * FROM places WHERE place LIKE ? LIMIT 1', (p[0],))
   latlon = []
   if q[0]['lat'] is not None:
      latlon.append(q[0]['lat'])
      latlon.append(q[0]['lon'])
   return latlon
