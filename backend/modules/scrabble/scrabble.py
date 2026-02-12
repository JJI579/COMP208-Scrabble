from pathlib import Path
import json
import requests
import twl
from sqlalchemy import text
from modules.database.database import get_session, init_db_sync, init_db
import asyncio


init_db_sync()
asyncio.run(init_db())
currentPath = Path.cwd()
pointsPath = currentPath / "scrabble_points.json"
pointsData = json.load(open(pointsPath))


defaultFiller = '|'
arr = [[defaultFiller for _ in range(15)] for _ in range(15)]

# return 
# {
# 	"points": 0,
# 	"word": "",
# 	"placement": [
# 		["id", "letter"]
# 	]
# }
class Player:

	def __init__(self) -> None:
		self.letters = []

	def append_letters(self, toGive: list[str]):
		for x in toGive:
			self.letters.append(x)

	def remove_letters(self, toTake: list[str]):
		for x in toTake:
			try:
				self.letters.remove(x)
			except ValueError:
				print(f"A letter to be removed is NOT in the players letter category | Letter: {x}")

	def can_make(self, word: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []):
		wordMap = {}
		availableCount = {}
		# TODO: consider preExisting
		for x in word:
			if x not in wordMap:
				wordMap[x] = 1
			else:
				wordMap[x] += 1
			availableCount[x] = self.letters.count(x)
		
		for key, val in wordMap.items():
			if key not in availableCount:
				return False
			if availableCount[key] < val:
				return False
			
		
class Scrabble:

	def __init__(self, arr) -> None:
		self.players = []
		self.gameTurn = 0
		self.game = arr
		self.firstPlaced = False
		pass

	def next_turn(self):
		if self.gameTurn < len(self.players):
			self.gameTurn += 1
		else:
			self.gameTurn = 0

	def get_cell(self, x: int, y: int):
		return self.game[y][x]
	
	def handle_placement(self, word: str, playerCode: str, preExisting: list[tuple[int, int]] = [], blanks: list[tuple[int, int]] = []):
		# player code is a string that they will use to verify that it is their turn, unless i use their bearer token / session_id to verify its from them?
		pass
	
	def convert_id_to_coordinate(self, squareID: int):
		x = squareID % 15
		y = squareID // 15
		return (x, y)
	
	def convert_coordinate_to_id(self, coordinate: tuple[int, int]):
		x = coordinate[0]
		y = coordinate[1]
		return (y * 15) + x

	def expand_vertically(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if y > 0 and y < 15:
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
				break

		return coordinates
	
	def expand_horizontally(self, position,):
		x = position[0]
		y = position[1]
		coordinates = []
		traversedBack = False
		while True:
			if x > 0 and x < 15:
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
				break

		return coordinates

	def place_word(self, word: str, position: tuple[int, int], direction: str, blanks: list[tuple[int, int]] = [], preExisting: list[tuple[int, int]] = []):
		wordCoordinates = []
		x = position[0]
		y = position[1]
		print("NEW ONE")
		tempPlaced = []
		for i in range(len(word)):
			if [x,y] not in preExisting:
				wordCoordinates.append([x, y])
			cellContents = self.get_cell(x, y)
			if cellContents != defaultFiller and (x, y) not in preExisting:
				print(x, y)
				print(self.get_cell(x, y))
				print(preExisting)
				# TODO: check if there is a word that works otherwise raise an issue.
				print("cell has already been taken!")
				for x, y in tempPlaced:
					self.game[y][x] = defaultFiller
				return
			else:
				# make it place already to imply that it can be used!
				if (x, y) not in preExisting:
					print("temp placed letter: ", word[i])
					self.game[y][x] = word[i]
					tempPlaced.append([x, y])
				else:
					if self.get_cell(x,y) == word[i]:
						print("missed letter: ", word[i])
					else:
						print(f"mis interpret of letter in preExisting: ({x},{y}) | Preexisting: {self.get_cell(x,y)} | Assumed to be: {word[i]}")
						for x, y in tempPlaced:
							self.game[y][x] = defaultFiller
						return

			if direction=="down":
				y+=1
			else:
				x+=1
		if not self.firstPlaced:
			# MAKE SURE IT CROSSES THE MIDDLE AS START
			if [7,7] not in wordCoordinates:
				return ""
			else:
				if self.check_word(word):
					# fine
					pass
				# check the word and allow placement.

		# we need to implement below on every letter, however if the direction of the letter is going down, then you only need to consider horizontal for each letter
		# and if the word placed was right, considered up and down along every letter, then see how that goes...
		# NOTE: pretty sure i have got it working...

		# below works for basic concatenation

		# assume there is no joining word till proved
		hasJoiningWord = False
		# assume every connection is a word until proven wrong
		# also we assume that they can provide us either a word, or not, if it is a word, prove wrong via connections, else it is fine.
		isWord = self.check_word(word)
		forceBreak = False
		points = 0
		for currentPosition in wordCoordinates:
			if forceBreak:
				break
			for testDirection in ['right', "down"]:
				if testDirection == "right":
					potentialWord = self.expand_horizontally(currentPosition)
				else:
					potentialWord = self.expand_vertically(currentPosition)
				print(potentialWord)
				testArray = potentialWord.copy()
				[testArray.remove(x) for x in wordCoordinates if x in testArray]
				if len(testArray) != 0:
					if testDirection == "down":
						potentialWord.sort(key=lambda x: x[1] )
					else:
						potentialWord.sort(key=lambda x: x[0] )
					wordOrdered = [[x, self.get_cell(x[0], x[1])] for x in potentialWord]
					wordString = ''.join([x[1] for x in wordOrdered])
					print(f'Checking word found: ' + wordString)
					if not self.check_word(wordString):
						isWord = False
						forceBreak = True
						print(f"{wordString} is not a word. ")
						break
					else:
						print(f"{wordString} is a word.")
						points+=self.calculate_points(wordOrdered, blanks)
						hasJoiningWord = True
						isWord = True
				else:
					if not self.firstPlaced:
						hasJoiningWord = True
						self.firstPlaced = True
		
		if len(word) == 7 and len(preExisting) == 0:
			points+=50 

		print(f'{hasJoiningWord} | {isWord} | {word} | Points: {points}')
		
		if self.firstPlaced:
			if not hasJoiningWord or not isWord: 
				pass
				# remove coordinates placed
				for x, y in tempPlaced:
					self.game[y][x] = defaultFiller
		# for l in wordOrdered:
		# 	print(l)

		# have to prove that it is connecting some kind of word to make it work.

		
	def calculate_points(self, wordOrdered: list[list], blanks: list[tuple[int, int]]):
		# THIS FUNCTION DOES NOT CONSIDER DOUBLE WORDS / LETTERS ETC.
		# blanks are coordinates of the letter.
		points = 0
		for tupe, letter in wordOrdered:
			if tupe not in blanks:
				# do not ignore
				points += pointsData[letter.upper()]
		return points

		# points = 0
		# for ind in range(len(word)):
		# 	if ind not in blanks:
		# 		points += pointsData[word[ind].upper()]
		# return points

	def print_board(self):
		for x in self.game:
			for i in x:
				print(i, end=" ")
			print()

	def check_word(self, word: str):
		return asyncio.run(self._check_word(word))
		# return twl.check(word)
		# resp = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word}')
		# respData = resp.json()
		# return not ('title' in respData)
	
	async def _check_word(self, word: str):
		async for session in get_session():
			resp = await session.execute(text("SELECT * FROM tblWords WHERE word = :word"), {"word": word})
			result = resp.scalar_one_or_none()
			print(f"Word Found: {result}")
			return result

# scrab = Scrabble([0, 1], arr)

# scrab.place_word("protege", (7,4), "down")
# scrab.place_word("epitaxes", (6,4), "right", preExisting=[(7,4)])
# scrab.place_word("taxes", (9,4), "down", preExisting=[(9,4)])
# # scrab.place_word("lazed", (10,3), "right", )
# # scrab.place_word("bet", (7,7), "down", [])
# # scrab.place_word("ee", (8,7), "right", [])
# scrab.place_word("best", (13,2), "down", preExisting=[(13, 4)])
# scrab.place_word("b", (12,3), "down")
# # scrab.place_word("e", (14,2), "right")

# scrab.print_board()
