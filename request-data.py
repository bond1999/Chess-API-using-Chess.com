import requests
import json
import simplejson
import datetime
import random
import os.path

## Edit these variables before running

# Set this to get data from a country, then save output from calling the function and 
# Country code for a specific country gotten from https://api.chess.com/pub/country/{CC}, where CC is the Country Code
# https://api.chess.com/pub/country/US, https://api.chess.com/pub/country/IN, https://api.chess.com/pub/country/RU
CountryCode = 'IN'

# Set this to define the Year you want to pull the games from
YYYY = '2021'

# Set this to define the Month you want to pull the games from
MM = '06'


##

# Global Variables

numberOfPlayers = 0

# Function to get List of players belonging to country/{CC}, CC is the Country Code
def downloadListOfPlayers(CountryCode):
	response = requests.get("https://api.chess.com/pub/country/" + CountryCode + "/players")
	if(list(response.json().keys())[0] == "status"): 
		print("Failed to download players from Country " + CountryCode + ". Please change the Country code!")
	else:
		json.dump(response.json(), open('playerlist' + CountryCode + '.json', 'w'))
		print("Sucessfully downloaded " + str(len(response.json()['players'])) + " currently online players from " + CountryCode +"!")

# Function to read the names of players from file and load stats for each
def loadPlayerStats(filename):
	with open(filename) as file:
		data = json.load(file)
	
	# for i in range(0, 50000):
	# 	playerName = random.choice(data['players'])
	for playerName in data['players']:
		if(playerName == 'bond1999'):
			global numberOfPlayers 
			numberOfPlayers += 1
		
			# Get rating	
			response = requests.get("https://api.chess.com/pub/player/" + playerName + "/stats")
			stats = response.json()	
			bestRating = 0
			
			# Uses primary game types to determine how good is a player and get a game based on those ratings
			for category in stats.keys():
				if category == 'chess_rapid' or category == 'chess_bullet' or category == 'chess_blitz':
					if(stats.get(category)['last']['rating'] > 1000 and checkIfRecent(stats.get(category)['last']['date'])):
						randomGame = getTotalChessGamesByMonth(playerName, YYYY, MM)

			writeToCSV(0, playerName, randomGame, getPGN(randomGame['pgn']))

	file.close();

# Function which writes data values directly to dataset.csv
def writeToCSV(sn, playerName, gameDetails, pgn):
	
	# Tags
	rated = gameDetails['rated']
	gameUsername = playerName
	gameURL = gameDetails['url']
	gameRules = gameDetails['rules']
	timeClass = gameDetails['time_class']
	timeControl = gameDetails['time_control']
	endTime = gameDetails['end_time']
	whiteUsername = gameDetails['white']['username']
	whiteRating = gameDetails['white']['rating']
	whiteResult = gameDetails['white']['result']
	blackUsername = gameDetails['black']['username']
	blackRating = gameDetails['black']['rating']
	blackResult = gameDetails['black']['result']
	Result = gameDetails['white']['result']
	ECO = 0
	ECOURL = "nothing"
	ECOName = "something"
	Moves = 64
	
	# Array to store all the tags for a single game
	Tags = [sn, rated, gameUsername, gameURL, gameRules, timeClass, timeControl, endTime, whiteUsername, 
	whiteRating, whiteResult, blackUsername, blackRating, blackResult, Result, ECO, ECOURL, ECOName, Moves]
	
	if(os.path.isfile('data.csv')):
		"Data being appended to file since file already exists"
	else:
		file = open('data.csv','w')
		file.write("sn,rated,gameUsername,gameURL,gameRules,timeClass,timeControl,endTime,whiteUsername,whiteRating,whiteResult,blackUsername,blackRating,blackResult,Result,ECO,ECOURL,ECOName,Moves\n")
		file.close()

	printJSON(gameDetails)
	print(Tags, len(Tags))

	file = open('data.csv','a')
	for tag in Tags:
		file.write(str(tag) + ",")
	file.write('\n')
	file.close()



# Function to parse and print JSON with Indentation
def printJSON(obj):
	text = json.dumps(obj, sort_keys = True, indent = 4)
	print(text)


# Function to get total games of a given player from specified YYYY and MM
def getTotalChessGamesByMonth(player, YYYY, MM):
	response = requests.get("https://api.chess.com/pub/player/" + player + "/games/" + YYYY + '/' + MM)
	data = response.json()
	print("%s had %s games" % (player, len(data['games'])))

	return random.choice(data['games'])
	
# Function to check if the last game was played since the defined YYYY and MM
def checkIfRecent(time):
	year = datetime.datetime.fromtimestamp(time).year
	month = datetime.datetime.fromtimestamp(time).month
	print(datetime.datetime.fromtimestamp(time))
	if(int(YYYY) == year and int(MM) <= month):
		return True

# Function to get a specific game's data from PGN
def getPGN(pgn):
	file = open('game.txt','w')
	file.write(pgn)
	file.close()
	file = open('game.txt','r')
	print(file.read())
	file.close()

# Main function to run the program
def main():
	downloadListOfPlayers(CountryCode)
	loadPlayerStats('playerlist' + CountryCode + '.json')
	print('numberOfPlayers = ' + str(numberOfPlayers))

# Run Program
main()




