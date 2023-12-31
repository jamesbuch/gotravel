# GoTravel Python Flask App

### Installation/setup
Use a python virtual environment for ease of installation and setup. To use this app
which makes use of the Chatterbot chat library, Python 3.7.9 or lower must be used
(the latest in the 3.7.x series _might_ work).

Set up a python virtual environment in the source directory:

``python -m venv .venv``

Activate:

``.venv\Scripts\activate``

Install packages from requirements:

``pip install -r requirements.txt``

To use the app, create a .env file in the travelapp directory, and supply an API key
for use with OpenWeatherMap, e.g.

OPENWEATHER_API_KEY=c123ab407d888a60b0c392b12345be9a


### Note about initializing the database

The database does not need to be initialized, but it can be re-created as an empty
database.  The current database contains helpful latitude and longitude coordinates
for some places on a pre-determined itinerary for the application.

This repository contains an instance directory and a ready-made sqlite database. It can
be overwritten by deleting the instance directory and running the command

``flask init-db``

### Running the application

The _.flaskenv_ file contains the app name, so it doesn't have to be specified on the
command line to reinitialize the database or run the app.

Start the Flask app:

``flask --run``

If using the ready-made database, a user with
email _james@example.com_ and password _example_ already exists. Note that if creating
a new database, some fetching of weather data may cause an error because latitude and
longitude coordinates must be specified for some locations. These coordinates for some
locations exist in the ready-made database.

Enter the email and password you registered,
and the app will render the main/index page.

From there, you can set up a new itinerary, view existing ones in the supplied sqlite
database, fetch weather information, and use the weather chat bot!

### Weather chat
The weather chat bot understands basic questions about weather and forecasts. It can
extract location information when asked about the _weather_, _temperature_ or
_forecast_ so long as the location is in a specific format, i.e. *_city_, _optional state_,
_country code_*.

For example, to retrieve the current weather, ask the chat bot a simple question like:

``What's the weather in Tamworth, NSW, Australia?``

To get a forecast, use the forecast keyword:

``Get forecast for London, UK``

### Screenshot

![GoTravel Screenshot](/gotravel-screenshot.png "GoTravel! Screenshot")
