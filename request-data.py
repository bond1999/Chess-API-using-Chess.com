import requests
import json

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

# Function to get List of players belonging to country/{CC}, CC is the Country Code
def downloadListOfPlayers(CountryCode):
	response = requests.get("https://api.chess.com/pub/country/" + CountryCode + "/players")
	if(list(response.json().keys())[0] == "status"): 
		print("Failed to download players from Country " + CountryCode + ". Please change the Country code!")
	else:
		data = json.dumps(response.json(), sort_keys = True, indent = 4)
		json.dump(data, open('playerlist' + CountryCode + '.json', 'w'))
		print("Sucessfully downloaded Currently Online players from " + CountryCode + ". JSON created!")
	
# Function to read the names of players from file and load stats for each
def loadPlayerStats(filename):
	file = open(filename,)
	data = json.load(file)
	for i in data['players']:
		print(i) # change here
	file.close();
	# Only loads names yet

# Function to parse and print JSON with Indentation
def printJSON(obj):
	text = json.dumps(obj, sort_keys = True, indent = 4)
	print(text)


# Function to get total games of a given player from specified YYYY and MM
def getTotalChessGamesByMonth(player, YYYY, MM):
	response = requests.get("https://api.chess.com/pub/player/" + player + "/games/" + YYYY + '/' + MM)
	data = response.json()
	# if(len(data['games']) > 120):
	print(len(data['games']))
	printJSON(data['games'][0])
	getChessGame(data['games'][0]['url'])
	# print(data['games'][0]['rules'])

# Function to get a specific game's data
def getChessGame(gameID):
	response = requests.get(gameID)
	print(response)
	data = response
	

# Main function to run the program
def main():
	downloadListOfPlayers(CountryCode)
	getTotalChessGamesByMonth('bond1999', YYYY, MM)


# Run Program
main()




