# Import libraries.
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

# Create a new ChatBot instance
bot = ChatBot(
    'My Bot',
    logic_adapters=[
        'chatterbot.logic.BestMatch',
        {
            'import_path': 'weather_adapter.WeatherLogicAdapter'
        }
    ]
)

# Example chats, it's sometimes difficult to extract a location to provide
# a useful answer; this is the job of the weather_adapter class
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

corpus_trainer = ChatterBotCorpusTrainer(bot)
corpus_trainer.train('chatterbot.corpus.english')

print(bot.get_response("Weather pls"))
print(bot.get_response("What's the weather?"))
print(bot.get_response("Forecast for"))
print(bot.get_response('Weather for Tamworth, NSW, AU'))

while True:
    try:
        bot_input = input("You: ")
        bot_response = bot.get_response(bot_input)
        print(f"{bot.name}: {bot_response}")
    except(KeyboardInterrupt, EOFError, SystemExit):
        break

