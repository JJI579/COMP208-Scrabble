from pathlib import Path
import json
import requests
import twl

currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))


defaultFiller = 'x'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

# return 
# {
# 	"points": 0,
# 	"word": "",
# 	"placement": [
# 		["id", "letter"]
# 	]
# }
class Scrabble:

	def __init__(self, players, arr) -> None:
		self.players: list[int] = players
		self.gameTurn = 0
		self.game = arr
		self.firstPlaced = False
		pass

	def add_player(self, userID: int):
		self.players.append(userID)

	def next_turn(self):
		if self.gameTurn < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0

	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def expand_vertically(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if y > 0 or y < 16:
				# perform
				if self.game[y][x] != defaultFiller:
					if [x, y] not in coordinates:
						coordinates.append([x, y])
					if traversedBack:
						y+=1
					else:
						y-=1
				else:
					# now go forwards
					if not traversedBack:
						traversedBack = True
						y+=1
					
					else:
						# this shouldve traversed backwards, and now finished going forwards
						break
			else:
				pass

		return coordinates
	
	def expand_horizontally(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if x > 0 or x < 16:
				# perform
				if self.game[y][x] != defaultFiller:
					if [x, y] not in coordinates:
						coordinates.append([x, y])
					if traversedBack:
						x+=1
					else:
						x-=1
				else:
					# now go forwards
					if not traversedBack:
						traversedBack = True
						x+=1
					
					else:
						# this shouldve traversed backwards, and now finished going forwards
						break

			else:
				pass

		return coordinates

	def place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[int] = [], preExisting: list[tuple[int, int]] = []):
		wordCoordinates = []
		x = position[0]
		y = position[1]
		print("NEW ONE")
		tempPlaced = []
		for i in range(len(word)):
			if [x,y] not in preExisting:
				wordCoordinates.append([x, y])
			cellContents = self.get_cell(x, y)
			print('-------------\n' + word)
			print(preExisting)
			print([x,y ] in preExisting)
			if cellContents != defaultFiller and [x, y] not in preExisting:
				print(x, y)
				print(self.get_cell(x, y))
				print("cell has already been taken!")
				# TODO: check if there is a word that works otherwise raise an issue.
				for x, y in tempPlaced:
					self.game[y][x] = defaultFiller
				return
			else:
				# make it place already to imply that it can be used!
				if [x, y] not in preExisting:
					print("temp placed letter: ", word[i])
					self.game[y][x] = word[i]
					tempPlaced.append([x, y])
				else:
					print("missed letter: ", word[i])
			if direction=="down":
				y+=1
			else:
				x+=1
		

		# we need to implement below on every letter, however if the direction of the letter is going down, then you only need to consider horizontal for each letter
		# and if the word placed was right, considered up and down along every letter, then see how that goes...

		# below works for basic concatenation

		# assume there is no joining word till proved
		hasJoiningWord = False
		# assume every connection is a word until proven wrong
		isWord = True
		for testDirection in ['right', "down"]:
			if testDirection == "right":
				potentialWord = self.expand_horizontally(position)
			else:
				potentialWord = self.expand_vertically(position)
			testArray = potentialWord.copy()
			# print("1")
			# print(potentialWord)
			[testArray.remove(x) for x in wordCoordinates if x in testArray]
			print(potentialWord)
			print(testArray)
			if len(testArray) != 0:
				if testDirection == "down":
					potentialWord.sort(key=lambda x: x[1] )
				else:
					potentialWord.sort(key=lambda x: x[0] )
				wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
				wordString = ''.join([x[1] for x in wordOrdered])
				print(f'string: ' + wordString)
				if not self.check_word(wordString):
					isWord = False
				else:
					print("this is true¬")
					hasJoiningWord = True
			else:
				if not self.firstPlaced:
					hasJoiningWord = True
					self.firstPlaced = True
		if not hasJoiningWord:
			# remove coordinates placed
			for x, y in tempPlaced:
				self.game[y][x] = defaultFiller
		# for l in wordOrdered:
		# 	print(l)

		# have to prove that it is connecting some kind of word to make it work.

		
	def calculate_points(self, word: str, blanks: list[int]):
		# THIS FUNCTION DOES NOT CONSIDER DOUBLE WORDS / LETTERS ETC.
		# blanks are indexes of the word
		points = 0
		for ind in range(len(word)):
			if ind not in blanks:
				points += pointsData[word[ind].upper()]
		return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()

	def check_word(self, word: str):
		return twl.check(word)
		# resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
		# respData = resp.json()
		# return not ('title' in respData)
	
scrab = Scrabble([0, 1], arr)

scrab.place_word("bet", (7,7), "down", [])
scrab.place_word("ee", (8,7), "right", [])
scrab.place_word("bet", (9,6), "down", preExisting=[[9,7]])

# scrab.place_word("b", (9,6), "down", [])
# scrab.place_word("t", (10,7), "down", [])
# scrab.place_word("ea", (10,8), "down", [])
# scrab.place_word("t", (10,10), "down", [])

scrab.print_board()

