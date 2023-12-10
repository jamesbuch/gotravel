from chatterbot.logic import LogicAdapter
import os
import re
from dotenv import load_dotenv
from datetime import datetime, date, time
import requests
from chatterbot.conversation import Statement

# Current weather, use get_forecast_openweathermap for a forecast
def get_weather_openweathermap(location):
   
	load_dotenv()
	api_key = os.getenv('OPENWEATHER_API_KEY')
	base_url = 'https://api.openweathermap.org/data/2.5/weather'
	params = {'q': location, 'appid': api_key, 'units': 'metric'}

	response = requests.get(base_url, params=params)
	data = response.json()

	# Extract relevant information from the API response
	if int(data['cod']) != 200:
		err = data['message']
		return f"Sorry, I got an error: {err} Please ask another question"

	temperature = data['main']['temp']
	condition = data['weather'][0]['description']

	ret = f"The current temperature in {location} is {temperature}°C, and the condition is {condition}."
	return ret


def get_forecast_openweathermap(location):

	load_dotenv()
	api_key = os.getenv('OPENWEATHER_API_KEY')
	base_url = 'https://api.openweathermap.org/data/2.5/forecast'
	params = {'q': location, 'appid': api_key, 'units': 'metric'}

	response = requests.get(base_url, params=params)
	data = response.json()

	if int(data['cod']) != 200:
		err = data['message']
		return f"Sorry, I got an error: {err} Please ask another question"

	# Extract relevant information from the API response
	forecast = []
	for item in data['list']:
		dt = datetime.fromtimestamp(item['dt'])
		dts = dt.strftime('%I:%M %p')
		if dts.find('8:00 AM') > -1 or dts.find('2:00 PM') > -1 or dts.find('8:00 PM') > -1:
			w = { 'datetime': dts, 'day': dt.strftime('%A'), 'temp': item['main']['temp'], 'feels_like': item['main']['feels_like'], 'min': item['main']['temp_min'], 'max': item['main']['temp_max'], 'main': item['weather'][0]['main'], 'desc': item['weather'][0]['description'].capitalize(), 'icon': 'https://openweathermap.org/img/wn/' + item['weather'][0]['icon'] + '@2x.png' }
			forecast.append(w)
 
	return forecast


def find_location_for_weather(question):
	regex = r"([a-zA-Z]+|\"[a-zA-Z ]+\")\s*,\s*[a-zA-Z]+\s*(,\s*[a-zA-Z]+)?"
	m = re.search(regex, question)
	if m:
		loc = m.group(0)
		return loc.replace('"', '')
	return None


def weather_question_check(statement):
	m = re.search('weather|forecast|temperature', statement, re.IGNORECASE)
	if m:
		return True
	return False


class WeatherLogicAdapter(LogicAdapter):
	def __init__(self, chatbot, **kwargs):
		super().__init__(chatbot, **kwargs)

	def can_process(self, statement):
		stat = statement.text.lower()
		return weather_question_check(stat)

	def process(self, input_statement, additional_response_selection_parameters):
		location = find_location_for_weather(str(input_statement))
  
		if location is None:
			weather_info = "I couldn't find a location for weather, for example `weather report for London, UK` or `what is the forecast for Tamworth, NSW, AU?`"
			# Create a response statement
			response_statement = Statement(weather_info)
			# Set the confidence level for the response
			response_statement.confidence = 0.5
			return response_statement

		m = re.search('weather|temperature', str(input_statement), re.IGNORECASE)
		weather_info = None
  
  		# Get the weather information using the OpenWeatherMap API, either single
		# line or multiline forecast response
		if m:
			weather_info = get_weather_openweathermap(location)
		else:
			m = re.search('forecast', str(input_statement), re.IGNORECASE)
			if m:
				weather_info = get_forecast_openweathermap(location)
			else:
				weather_info = "I couldn't find a keyword, for example `weather report for London, UK` or `what is the forecast for Tamworth, NSW, AU?`"
				# Create a response statement
				response_statement = Statement(weather_info)
				# Set the confidence level for the response
				response_statement.confidence = 0.5
				return response_statement

		# Create a response statement
		response_statement = Statement(weather_info)

		# Set the confidence level for the response
		response_statement.confidence = 1.0

		return response_statement
