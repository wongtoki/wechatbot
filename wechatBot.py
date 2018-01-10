#!/usr/bin/env python3.5
from wxpy import *
import os 
import sys
import json
import datetime
import requests
try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

class Weather:
	temp = 0
	weather = "sunny"


configPath = input("Enter config path (default:'config.json'): \n")
if configPath == "":
	configPath = "config.json"

config = json.load(open(configPath))


#Logging your bot
bot = Bot(cache_path = True,console_qr = 1)

#Get your friends and groups
if bot:
	friends = bot.friends()
	groups = bot.groups()

#Reply to messages
def SendMSG(message):
	target = message.chat
	response = GetResponseText(message.text,message.chat.name)
	target.send_msg("Toki's robot says: \""+response + "\"")

#Message listener
@bot.register(groups)
def reply_to_group(msg):
	if msg.is_at:
		SendMSG(msg)

#Message listener
@bot.register(friends)
def reply_my_friend(msg):
	SendMSG(msg)

#Tread join, enters python command line
embed()

#Test Dialogue Flow response
def TestResponse(message):
	print(GetResponseText(message,"Test"))

#Get Dialogue Flow response
def GetResponseText(text, sid):		
	
	CLIENT_ACCESS_TOKEN = str(config['DialogueFlowAPI'])
	ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

	request = ai.text_request()
	request.lang = 'en'
	request.session_id = sid
	
	request.query = text

	response = json.loads(request.getresponse().read().decode('utf-8'))

	try:
		intent = response['result']['metadata']['intentName']
		parameters = response['result']['parameters']
	except Exception:
		return str(response['result']['fulfillment']['speech'])
	
	if intent == "ask_weather" and parameters['geo-city'] != "":
		weather = GetWeather(parameters['geo-city'],parameters['date'])
		if weather == "":
			return str(response['result']['fulfillment']['speech'])
		else:
			return weather
		

	return str(response['result']['fulfillment']['speech'])


# Get weather api
def GetWeather(location, date):

	apiKey = config['WeatherAPI']
	currentDate = datetime.date.today()
	if date == currentDate or date == "":
		data = requests.get('http://api.openweathermap.org/data/2.5/weather?q='+location+'&appid=' + apiKey).json()
		temp = round(float(data['main']['temp']) - 273.15, 2) #convert to celsius 
		weather = str(data['weather'][0]['main']).lower()
		return "The weather today in "+location+" is " + weather + " with a temperature of " +str(temp)+ " degrees."
	else:
		forecast = requests.get('http://api.openweathermap.org/data/2.5/forecast?q='+location+'&appid=' + apiKey).json()
		
		for x in forecast['list']:
			if str(x['dt_txt'])[0:10] == date:
				canGetWeather = True
				forecast_temp = round(float(x['main']['temp_max']) - 273.15, 2)
				forecast_weather = str(x['weather'][0]['main']).lower()
				break
			canGetWeather = False

		if not canGetWeather:
			return ""

		if str(datetime.date.today() + datetime.timedelta(days=1)) == date:
			return "The weather tomorrow in "+location+" will be " + forecast_weather + " with a temperature of " +str(forecast_temp)+ " degrees."
		else:
			return "The weather on "+date+" in "+location+" will be " + forecast_weather + " with a temperature of " +str(forecast_temp)+ " degrees."

	return ""








