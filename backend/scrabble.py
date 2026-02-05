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

	def place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[int]):
		wordCoordinates = []
		x = position[0]
		y = position[1]
		for i in range(len(word)):
			wordCoordinates.append([x, y])
			if self.get_cell(x, y) != defaultFiller:
				print("cell has already been taken!")
				# TODO: check if there is a word that works otherwise raise an issue.
				return
			else:
				# make it place already to imply that it can be used!
				self.game[y][x] = word[i]
			if direction=="down":
				y+=1
			else:
				x+=1
		
		potentialWord = self.expand_vertically(position)
		if direction == "down":
			potentialWord.sort(key=lambda x: x[1] )
		else:
			potentialWord.sort(key=lambda x: x[0] )
		wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
		print(wordOrdered)
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
# scrab.test_word("bet", (7,7), "down", [])
scrab.place_word("ee", (8,7), "right", [])
# scrab.test_word("te", (9,5), "down", [])
# scrab.test_word("tit", (3,4), "down", [])
# scrab.test_word("gap", (2,1), "down", [])
# scrab.test_word("t", (3,4), "down", [])

scrab.print_board()

