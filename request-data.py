import requests
import json
import simplejson
import datetime
import random
import os
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
	
	i = 0
	if(os.path.isfile('data.csv')):
		with open('data.csv', 'rb') as f:
		    f.seek(-2, os.SEEK_END)
		    while f.read(1) != b'\n':
		        f.seek(-2, os.SEEK_CUR)
		    last_line = f.readline().decode()
		i = last_line.split(',')[0]
		print("Data being appended to file already exists! Resuming operation..\n")
	else:
		file = open('data.csv','w')
		file.write("sn, gameURL, rated, startTime, endTime, halfMoves, victoryReason, gameResult, winner, timeControl, whiteUsername, whiteRating, blackUsername, blackRating, moves, endingFEN, ECO, ECOURL, ECOName\n")
		file.close()
		print("New data.csv created! Starting Operation")	

	for i in range(0, 300000):
		playerName = random.choice(data['players'])	
		global numberOfPlayers 
		numberOfPlayers += 1
	
		# Get rating	
		response = requests.get("https://api.chess.com/pub/player/" + playerName + "/stats")
		stats = response.json()	
		bestRating = 0
		
		# Uses primary game types to determine how good is a player and get a game based on those ratings
		for category in stats.keys():
			if category == 'chess_rapid' or category == 'chess_bullet' or category == 'chess_blitz':
				if(stats.get(category)['last']['rating'] > 1600 and checkIfRecent(stats.get(category)['last']['date'])):
					print(i, end = " ")
					randomGame = getTotalChessGamesByMonth(playerName, YYYY, MM)
					if(randomGame == "skip"):
						print("skipped")
					else:
						writeToCSV(i, playerName, randomGame, getPGN(randomGame['pgn']))
					break		
		

	file.close();

# Function which writes data values directly to dataset.csv
def writeToCSV(sn, playerName, gameDetails, pgn):
	
	# Tags from gameDetails
	rated = gameDetails['rated']
	gameUsername = playerName
	gameURL = gameDetails['url'][32:]
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
	
	file = open('game.txt','r')
	lines = [line.strip("\n") for line in file.readlines() if line != "\n"]
	
	gameResult = "0-0"
	startTime = 0
	ECO = 0
	ECOURL = "nothing"
	ECOName = "something"
	halfMoves = 64
	endingFEN = "blank"
	victoryReason = ""
	moves = ""
	for line in lines:
		if(line[0] == '['):
			line = line[1:len(line)-1]
			data = line.split(" ", 1)
			# Assigning data from PGN
			if(data[0] == "Result"):
				gameResult = data[1].strip('"')
			if(data[0] == "CurrentPosition"):
				endingFEN = data[1].strip('"')
			if(data[0] == "ECO"):
				ECO = data[1].strip('"')
			if(data[0] == "ECOUrl"):
				ECOURL = data[1].strip('"')
				ECOName = data[1].strip('"')[31:]
			if(data[0] == "Date"):
				startTime = datetime.datetime.strptime(data[1].strip('"'), '%Y.%m.%d')
			if(data[0] == "StartTime"):
				startTime += datetime.timedelta(hours = int(data[1].strip('"').split(':')[0]))
				startTime += datetime.timedelta(minutes = int(data[1].strip('"').split(':')[1]))
				startTime += datetime.timedelta(seconds = int(data[1].strip('"').split(':')[2]))
				startTime = startTime.timestamp()
			if(data[0] == "EndDate"):
				endTime = datetime.datetime.strptime(data[1].strip('"'), '%Y.%m.%d')
			if(data[0] == "EndTime"):
				endTime += datetime.timedelta(hours = int(data[1].strip('"').split(':')[0]))
				endTime += datetime.timedelta(minutes = int(data[1].strip('"').split(':')[1]))
				endTime += datetime.timedelta(seconds = int(data[1].strip('"').split(':')[2]))
				endTime = endTime.timestamp()
			if(data[0] == "Termination"):
				victoryReason = data[1].strip('"')
		
		elif (line[0] == '1'):	
			for i in range(0, len(line)):
				if(line[i] == '.' and line[i+1] == ' ' and line[i-1] != '.'):
					i += 2
					while(line[i] != ' '):
						moves += line[i]
						i += 1
					moves += " "
				if(line[i] == '.' and line[i+1] == '.' and line[i+2] == '.' and line[i+3] == ' '):
					i += 4
					while(line[i] != ' '):
						moves += line[i]
						i += 1
					moves += " "
		
		moves = moves[0:len(moves)-1]
		halfMoves = len(moves.split(' '))

				

	

	if(gameResult == "1-0"):
		winner = "white"
	elif(gameResult == "0-1"):
		winner = "black"
	else:
		winner = "draw"


	# Array to store all the tags for a single game
	Tags = [sn, gameURL, rated, startTime, endTime, halfMoves, victoryReason, gameResult, winner, timeControl, 
	whiteUsername, whiteRating, blackUsername, blackRating, moves, endingFEN, ECO, ECOURL, ECOName]
	
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
	if(len(data['games']) < 50):
		return "skip"
	else:
		return random.choice(data['games'])
	
# Function to check if the last game was played since the defined YYYY and MM
def checkIfRecent(time):
	year = datetime.datetime.fromtimestamp(time).year
	month = datetime.datetime.fromtimestamp(time).month
	if(int(YYYY) == year and int(MM) <= month):
		return True

# Function to get a specific game's data from PGN
def getPGN(pgn):
	file = open('game.txt','w')
	file.write(pgn)
	file.close()

# Main function to run the program
def main():
	downloadListOfPlayers(CountryCode)
	loadPlayerStats('playerlist' + CountryCode + '.json')
	print('numberOfPlayers = ' + str(numberOfPlayers))

# Run Program
main()




