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

Start the Flask app:

``flask --run``

To really use the app, register an email and a password. Visit the register link, fill
out the form, then click the Login link.  Enter the email and password you registered,
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

